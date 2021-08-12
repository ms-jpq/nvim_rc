from asyncio.tasks import as_completed
from itertools import chain
from json import dumps, loads
from os import environ, linesep, pathsep
from pathlib import Path
from platform import uname
from shlex import join
from shutil import get_terminal_size, which
from sys import executable, stderr
from time import time
from typing import (
    AsyncIterator,
    Awaitable,
    Iterator,
    Mapping,
    Sequence,
    Tuple,
    TypedDict,
)

from pynvim.api.nvim import Nvim
from pynvim_pp.api import ask_mc
from std2.asyncio.subprocess import ProcReturn, call

from ..config.fmt import fmt_specs
from ..config.install import ScriptSpec
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import GitPkgSpec, pkg_specs
from ..config.tools import tool_specs
from ..consts import (
    BIN_DIR,
    GO_DIR,
    INSTALL_SCRIPT,
    INSTALL_SCRIPTS_DIR,
    LIB_DIR,
    NPM_DIR,
    TMP_DIR,
    UPDATE_LOG,
    VARS_DIR,
    VENV_DIR,
    VIM_DIR,
)
from ..registery import LANG
from ..workspace.terminal import open_term
from .rtp import p_name


class _PackagesJson(TypedDict):
    dependencies: Mapping[str, str]
    devDependencies: Mapping[str, str]


def _pip_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.pip
    for i_spec in linter_specs:
        yield from i_spec.install.pip
    for f_spec in fmt_specs:
        yield from f_spec.install.pip
    for t_spec in tool_specs:
        yield from t_spec.pip


def _npm_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.npm
    for i_spec in linter_specs:
        yield from i_spec.install.npm
    for f_spec in fmt_specs:
        yield from f_spec.install.npm
    for t_spec in tool_specs:
        yield from t_spec.npm


def _go_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.go
    for i_spec in linter_specs:
        yield from i_spec.install.go
    for f_spec in fmt_specs:
        yield from f_spec.install.go
    for t_spec in tool_specs:
        yield from t_spec.go


def _script_specs() -> Iterator[Tuple[str, ScriptSpec]]:
    for l_spec in lsp_specs:
        yield l_spec.bin, l_spec.install.script
    for i_spec in linter_specs:
        yield i_spec.bin, i_spec.install.script
    for f_spec in fmt_specs:
        yield f_spec.bin, f_spec.install.script


def _installable(script_spec: ScriptSpec) -> bool:
    return bool(script_spec.file and all(map(which, script_spec.required)))


SortOfMonoid = Sequence[Tuple[str, ProcReturn]]


def _git() -> Iterator[Awaitable[SortOfMonoid]]:
    VIM_DIR.mkdir(parents=True, exist_ok=True)
    cmd = "git"

    if which(cmd):
        for spec in pkg_specs:

            async def cont(spec: GitPkgSpec) -> SortOfMonoid:
                async def cont() -> AsyncIterator[Tuple[str, ProcReturn]]:
                    location = p_name(spec.uri)
                    if location.is_dir():
                        p1 = await call(
                            cmd,
                            "pull",
                            "--recurse-submodules",
                            *(("origin", spec.branch) if spec.branch else ()),
                            cwd=location,
                            check_returncode=set(),
                        )
                    else:
                        p1 = await call(
                            cmd,
                            "clone",
                            "--depth=1",
                            "--recurse-submodules",
                            "--shallow-submodules",
                            *(("--branch", spec.branch) if spec.branch else ()),
                            "--",
                            spec.uri,
                            location,
                            check_returncode=set(),
                        )
                    yield spec.uri, p1

                    pkg = spec.script
                    if not p1.code and _installable(pkg):
                        p2 = await call(
                            INSTALL_SCRIPTS_DIR / pkg.file,
                            env=pkg.env,
                            cwd=location,
                            check_returncode=set(),
                        )
                        yield "", p2

                return [rt async for rt in cont()]

            yield cont(spec.git)


def _pip() -> Iterator[Awaitable[SortOfMonoid]]:
    VENV_DIR.mkdir(parents=True, exist_ok=True)
    specs = tuple(_pip_specs())

    if specs:

        async def cont() -> SortOfMonoid:
            p = await call(
                executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--target",
                VENV_DIR,
                "--",
                *specs,
                check_returncode=set(),
            )
            return (("", p),)

        yield cont()


def _npm() -> Iterator[Awaitable[SortOfMonoid]]:
    NPM_DIR.mkdir(parents=True, exist_ok=True)
    packages_json = NPM_DIR / "package.json"
    package_lock = NPM_DIR / "package-lock.json"

    async def cont() -> SortOfMonoid:
        async def cont() -> AsyncIterator[Tuple[str, ProcReturn]]:
            cmd = "npm"
            if which(cmd):
                packages_json.unlink(missing_ok=True)
                p1 = await call(
                    cmd,
                    "init",
                    "--yes",
                    cwd=NPM_DIR,
                    check_returncode=set(),
                )
                p = ProcReturn(
                    prog=p1.prog, args=p1.args, code=p1.code, out=b"", err=p1.err
                )
                yield "", p

                if not p1.code:
                    package_lock.unlink(missing_ok=True)
                    json: _PackagesJson = loads(packages_json.read_text())
                    json["dependencies"] = {}
                    json["devDependencies"] = {
                        key: "*"
                        for key in chain(
                            json.get("devDependencies", {}).keys(), _npm_specs()
                        )
                    }
                    packages_json.write_text(
                        dumps(json, check_circular=False, ensure_ascii=False, indent=2)
                    )

                    p2 = await call(
                        cmd,
                        "install",
                        "--upgrade",
                        cwd=NPM_DIR,
                        check_returncode=set(),
                    )
                    yield ("", p2)

        return [rt async for rt in cont()]

    yield cont()


def _go() -> Iterator[Awaitable[SortOfMonoid]]:
    GO_DIR.mkdir(parents=True, exist_ok=True)
    cmd = "go"

    if which(cmd):

        async def cont() -> SortOfMonoid:
            p = await call(
                cmd,
                "get",
                "--",
                *_go_specs(),
                env={"GO111MODULE": "on", "GOPATH": str(GO_DIR)},
                cwd=VARS_DIR,
                check_returncode=set(),
            )
            return (("", p),)

        yield cont()


def _script() -> Iterator[Awaitable[SortOfMonoid]]:
    for path in (BIN_DIR, LIB_DIR, TMP_DIR):
        path.mkdir(parents=True, exist_ok=True)

    sys = uname()
    for bin, pkg in _script_specs():

        async def cont(bin: str, pkg: ScriptSpec) -> SortOfMonoid:
            env = {
                "PATH": pathsep.join(
                    (
                        str(INSTALL_SCRIPTS_DIR),
                        environ["PATH"],
                    )
                ),
                "ARCH": sys.machine,
                "OS": sys.system,
                "BIN": str(BIN_DIR / bin),
                "LIB": str(LIB_DIR / bin),
            }
            p = await call(
                INSTALL_SCRIPTS_DIR / pkg.file,
                env={**env, **pkg.env},
                cwd=TMP_DIR,
                check_returncode=set(),
            )
            return (("", p),)

        if _installable(pkg):
            yield cont(bin, pkg)


async def install() -> int:
    cols, _ = get_terminal_size((80, 40))
    sep = cols * "="

    has_error = False
    for fut in as_completed(chain(_git(), _pip(), _npm(), _go(), _script())):
        for debug, proc in await fut:
            args = join(map(str, chain((proc.prog,), proc.args)))
            if proc.code == 0:
                msg = LANG("proc succeeded", args=args)
                print(
                    msg, debug, proc.err.decode(), proc.out.decode(), sep, sep=linesep
                )
            else:
                has_error = True
                msg = LANG("proc failed", code=proc.code, args=args)
                print(
                    msg,
                    debug,
                    proc.out.decode(),
                    proc.err.decode(),
                    sep,
                    sep=linesep,
                    file=stderr,
                )

    return has_error


def maybe_install(nvim: Nvim) -> None:
    UPDATE_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        coded = UPDATE_LOG.read_text()
    except FileNotFoundError:
        before = 0.0
    else:
        before = float(coded)

    now = time()
    diff = now - before
    if diff > (7 * 24 * 3600):
        ans = ask_mc(
            nvim,
            question=LANG("update?"),
            answers=LANG("ask yes/no"),
            answer_key={1: 1, 2: 2},
        )
        if ans:
            coded = str(now)
            UPDATE_LOG.write_text(coded)

        if ans == 1:
            open_term(
                nvim, Path(executable).resolve(), INSTALL_SCRIPT, "deps", "packages"
            )
