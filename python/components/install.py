from asyncio.tasks import as_completed
from itertools import chain
from json import dumps, loads
from os import environ, linesep, pathsep
from os.path import normcase
from pathlib import Path, PurePath
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
    MutableSequence,
    Sequence,
    Tuple,
    TypedDict,
)

from pynvim.api.nvim import Nvim
from pynvim_pp.api import ask_mc
from pynvim_pp.lib import decode
from std2.asyncio.subprocess import call
from std2.subprocess import ProcReturn

from ..config.fmt import fmt_specs
from ..config.install import ScriptSpec
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import GitPkgSpec, pkg_specs
from ..config.tools import tool_specs
from ..consts import (
    BIN_DIR,
    GEM_DIR,
    GO_DIR,
    INSTALL_SCRIPT,
    INSTALL_SCRIPTS_DIR,
    LIB_DIR,
    NPM_DIR,
    PIP_DIR,
    TMP_DIR,
    UPDATE_LOG,
    VARS_DIR,
    VIM_DIR,
)
from ..registery import LANG
from ..workspace.terminal import open_term
from .rtp import p_name

_SortOfMonoid = Sequence[Tuple[str, ProcReturn]]


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
    yield from tool_specs.pip


def _gem_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.gem
    for i_spec in linter_specs:
        yield from i_spec.install.gem
    for f_spec in fmt_specs:
        yield from f_spec.install.gem
    yield from tool_specs.gem


def _npm_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.npm
    for i_spec in linter_specs:
        yield from i_spec.install.npm
    for f_spec in fmt_specs:
        yield from f_spec.install.npm
    yield from tool_specs.npm


def _go_specs() -> Iterator[str]:
    for l_spec in lsp_specs:
        yield from l_spec.install.go
    for i_spec in linter_specs:
        yield from i_spec.install.go
    for f_spec in fmt_specs:
        yield from f_spec.install.go
    yield from tool_specs.go


def _script_specs() -> Iterator[Tuple[str, ScriptSpec]]:
    for l_spec in lsp_specs:
        yield l_spec.bin, l_spec.install.script
    for i_spec in linter_specs:
        yield i_spec.bin, i_spec.install.script
    for f_spec in fmt_specs:
        yield f_spec.bin, f_spec.install.script
    for t_spec in tool_specs.script:
        yield "", t_spec


def _git() -> Iterator[Awaitable[_SortOfMonoid]]:
    VIM_DIR.mkdir(parents=True, exist_ok=True)

    if git := which("git"):

        async def cont(spec: GitPkgSpec) -> _SortOfMonoid:
            async def cont() -> AsyncIterator[Tuple[str, ProcReturn]]:
                assert git
                location = p_name(spec.uri)
                if location.is_dir():
                    p1 = await call(
                        git,
                        "pull",
                        "--recurse-submodules",
                        *(("origin", spec.branch) if spec.branch else ()),
                        cwd=location,
                        check_returncode=set(),
                    )
                else:
                    p1 = await call(
                        git,
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

                if not p1.code and spec.call:
                    p2 = await call(
                        *spec.call,
                        cwd=location,
                        check_returncode=set(),
                    )
                    yield "", p2

            return [rt async for rt in cont()]

        for spec in pkg_specs:
            yield cont(spec.git)


def _pip() -> Iterator[Awaitable[_SortOfMonoid]]:
    specs = {*_pip_specs()}

    if pip := which("pip") and specs:

        async def cont() -> _SortOfMonoid:
            assert pip
            p = await call(
                pip,
                "install",
                "--upgrade",
                "--user",
                "--",
                *specs,
                check_returncode=set(),
                env={"PYTHONUSERBASE": normcase(PIP_DIR)},
            )
            return (("", p),)

        yield cont()


def _gem() -> Iterator[Awaitable[_SortOfMonoid]]:
    specs = {*_gem_specs()}

    if gem := which("gem") and specs:

        async def cont() -> _SortOfMonoid:
            assert gem
            p = await call(
                gem,
                "install",
                "--install-dir",
                GEM_DIR / "gems",
                "--bindir",
                GEM_DIR / "bin",
                *specs,
                check_returncode=set(),
            )
            return (("", p),)

        yield cont()


def _npm() -> Iterator[Awaitable[_SortOfMonoid]]:
    NPM_DIR.mkdir(parents=True, exist_ok=True)
    packages_json = NPM_DIR / "package.json"
    package_lock = NPM_DIR / "package-lock.json"

    if which("node") and (npm := which("npm")):

        async def cont() -> _SortOfMonoid:
            async def cont() -> AsyncIterator[Tuple[str, ProcReturn]]:
                assert npm
                packages_json.unlink(missing_ok=True)

                p1 = await call(
                    npm,
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
                        for key in chain(json.get("devDependencies", {}), _npm_specs())
                    }
                    packages_json.write_text(
                        dumps(json, check_circular=False, ensure_ascii=False, indent=2)
                    )

                    p2 = await call(
                        npm,
                        "install",
                        "--no-package-lock",
                        "--upgrade",
                        cwd=NPM_DIR,
                        check_returncode=set(),
                    )
                    yield ("", p2)

            return [rt async for rt in cont()]

        yield cont()


def _go() -> Iterator[Awaitable[_SortOfMonoid]]:
    GO_DIR.mkdir(parents=True, exist_ok=True)
    specs = {*_go_specs()}

    if go := which("go"):

        async def cont(spec: str) -> _SortOfMonoid:
            assert go
            p = await call(
                go,
                "install",
                "--",
                spec,
                env={"GO111MODULE": "on", "GOPATH": normcase(GO_DIR)},
                cwd=VARS_DIR,
                check_returncode=set(),
            )
            return (("", p),)

        for spec in specs:
            yield cont(spec)


def _script() -> Iterator[Awaitable[_SortOfMonoid]]:
    for path in (BIN_DIR, LIB_DIR, TMP_DIR):
        path.mkdir(parents=True, exist_ok=True)

    sys = uname()
    for bin, pkg in _script_specs():

        async def cont(path: PurePath, bin: str, pkg: ScriptSpec) -> _SortOfMonoid:
            env = {
                "PATH": pathsep.join(
                    (
                        normcase(INSTALL_SCRIPTS_DIR),
                        environ["PATH"],
                    )
                ),
                "ARCH": sys.machine,
                "OS": sys.system,
                "BIN": normcase(BIN_DIR / bin),
                "LIB": normcase(LIB_DIR / bin),
            }
            p = await call(
                path,
                env={**env, **pkg.env},
                cwd=TMP_DIR,
                check_returncode=set(),
            )
            return (("", p),)

        if pkg.file and all(map(which, pkg.required)):
            if s_path := which(INSTALL_SCRIPTS_DIR / pkg.file):
                yield cont(PurePath(s_path), bin=bin, pkg=pkg)


async def install() -> int:
    cols, _ = get_terminal_size()
    sep = cols * "="

    errors: MutableSequence[str] = []
    tasks = chain(_git(), _pip(), _gem(), _npm(), _go(), _script())
    for fut in as_completed(tasks):
        for debug, proc in await fut:
            args = join(map(str, chain((proc.prog,), proc.args)))
            if proc.code == 0:
                msg = LANG("proc succeeded", args=args)
                print(msg, debug, decode(proc.err), decode(proc.out), sep, sep=linesep)
            else:
                errors.append(args)
                msg = LANG("proc failed", code=proc.code, args=args)
                print(
                    msg,
                    debug,
                    decode(proc.err),
                    decode(proc.out),
                    sep,
                    sep=linesep,
                    file=stderr,
                )

    if errors:
        print(linesep.join(errors))
    return bool(errors)


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
                nvim,
                Path(executable).resolve(strict=True),
                INSTALL_SCRIPT,
                "deps",
                "packages",
            )
