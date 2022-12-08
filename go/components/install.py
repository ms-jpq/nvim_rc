from asyncio.tasks import as_completed
from itertools import chain
from json import dumps, loads
from os import environ, linesep, pathsep, sep
from os.path import normcase
from pathlib import Path, PurePath
from shlex import join, split
from shutil import get_terminal_size, which
from subprocess import CompletedProcess
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
from venv import EnvBuilder

from pynvim_pp.lib import decode
from pynvim_pp.nvim import Nvim
from std2.asyncio.subprocess import call
from std2.platform import OS, os
from std2.string import removeprefix

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
    RT_SCRIPTS,
    TMP_DIR,
    UPDATE_LOG,
    VARS_DIR,
    VIM_DIR,
)
from ..registery import LANG
from ..workspace.terminal import open_term
from .rtp import p_name

_SortOfMonoid = Sequence[Tuple[str, CompletedProcess]]


class _PackagesJson(TypedDict):
    dependencies: Mapping[str, str]
    devDependencies: Mapping[str, str]


_GEMS = GEM_DIR / "gems"


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
            async def cont() -> AsyncIterator[Tuple[str, CompletedProcess]]:
                assert git
                location = p_name(spec.uri)
                if location.is_dir():
                    p1 = await call(
                        git,
                        "pull",
                        "--recurse-submodules",
                        "--no-tags",
                        *(("origin", spec.branch) if spec.branch else ()),
                        cwd=location,
                        capture_stderr=False,
                        check_returncode=set(),
                    )
                else:
                    p1 = await call(
                        git,
                        "clone",
                        "--recurse-submodules",
                        "--depth=1",
                        "--shallow-submodules",
                        *(("--branch", spec.branch) if spec.branch else ()),
                        "--",
                        spec.uri,
                        location,
                        capture_stderr=False,
                        check_returncode=set(),
                    )
                yield spec.uri, p1

                if not p1.returncode and spec.call:
                    p2 = await call(
                        *spec.call,
                        cwd=location,
                        capture_stderr=False,
                        check_returncode=set(),
                    )
                    yield "", p2

            return [rt async for rt in cont()]

        for spec in pkg_specs:
            yield cont(spec.git)


def _pip() -> Iterator[Awaitable[_SortOfMonoid]]:
    if specs := {*_pip_specs()}:
        builder = EnvBuilder(
            system_site_packages=False,
            with_pip=True,
            upgrade=True,
            symlinks=os is not OS.windows,
            clear=False,
        )
        builder.create(PIP_DIR)
        pip = PIP_DIR / RT_SCRIPTS / "pip"

        async def cont() -> _SortOfMonoid:
            p = await call(
                pip,
                "install",
                "--require-virtualenv",
                "--upgrade",
                "--",
                *specs,
                capture_stderr=False,
                check_returncode=set(),
            )
            return (("", p),)

        yield cont()


def _gem() -> Iterator[Awaitable[_SortOfMonoid]]:
    if (
        (gem := which("gem"))
        and (specs := {*_gem_specs()})
        and (
            os != OS.macos
            or not PurePath(gem).is_relative_to(PurePath(sep) / "usr" / "bin")
        )
    ):

        async def cont() -> _SortOfMonoid:
            assert gem
            p = await call(
                gem,
                "install",
                "--install-dir",
                _GEMS,
                *specs,
                capture_stderr=False,
                check_returncode=set(),
            )
            return (("", p),)

        yield cont()


async def _binstub() -> _SortOfMonoid:
    p = await call(
        executable,
        INSTALL_SCRIPTS_DIR / "binstub",
        "--src",
        _GEMS,
        "--dst",
        GEM_DIR / "bin",
        capture_stderr=False,
        check_returncode=set(),
    )
    return (("", p),)


def _npm() -> Iterator[Awaitable[_SortOfMonoid]]:
    NPM_DIR.mkdir(parents=True, exist_ok=True)
    packages_json = NPM_DIR / "package.json"
    package_lock = NPM_DIR / "package-lock.json"

    if which("node") and (npm := which("npm")) and (specs := {*_npm_specs()}):

        async def cont() -> _SortOfMonoid:
            async def cont() -> AsyncIterator[Tuple[str, CompletedProcess]]:
                assert npm
                packages_json.unlink(missing_ok=True)

                p1 = await call(
                    npm,
                    "init",
                    "--yes",
                    cwd=NPM_DIR,
                    capture_stderr=False,
                    check_returncode=set(),
                )
                p = CompletedProcess(
                    args=p1.args,
                    returncode=p1.returncode,
                    stdout=b"",
                    stderr=p1.stderr,
                )
                yield "", p

                if not p.returncode:
                    package_lock.unlink(missing_ok=True)
                    json: _PackagesJson = loads(packages_json.read_text())
                    json["dependencies"] = {}
                    json["devDependencies"] = {
                        key: "*"
                        for key in chain(json.get("devDependencies", {}), specs)
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
                        capture_stderr=False,
                        check_returncode=set(),
                    )
                    yield ("", p2)

            return [rt async for rt in cont()]

        yield cont()


def _go() -> Iterator[Awaitable[_SortOfMonoid]]:
    GO_DIR.mkdir(parents=True, exist_ok=True)

    if (go := which("go")) and (specs := {*_go_specs()}):

        async def cont(spec: str) -> _SortOfMonoid:
            assert go
            p = await call(
                go,
                "install",
                "--",
                spec,
                env={"GO111MODULE": "on", "GOPATH": normcase(GO_DIR)},
                cwd=VARS_DIR,
                capture_stderr=False,
                check_returncode=set(),
            )
            return (("", p),)

        for spec in specs:
            yield cont(spec)


def _script() -> Iterator[Awaitable[_SortOfMonoid]]:
    for path in (BIN_DIR, LIB_DIR, TMP_DIR):
        path.mkdir(parents=True, exist_ok=True)

    for bin, pkg in _script_specs():

        async def cont(path: Path, bin: str, pkg: ScriptSpec) -> _SortOfMonoid:
            env = {
                "PATH": pathsep.join(
                    (
                        normcase(INSTALL_SCRIPTS_DIR),
                        environ["PATH"],
                    )
                ),
                "BIN": normcase(BIN_DIR / bin),
                "LIB": normcase(LIB_DIR / bin),
            }
            if os is OS.windows and (tramp := which("env")):
                with path.open("r", encoding="ascii") as f:
                    l1 = next(f, "")
                argv = (tramp, *split(removeprefix(l1, "#!/usr/bin/env")))
            else:
                argv = (path,)

            p = await call(
                *argv,
                env={**env, **pkg.env},
                cwd=TMP_DIR,
                capture_stderr=False,
                check_returncode=set(),
            )
            return (("", p),)

        if pkg.file and all(map(which, pkg.required)):
            if s_path := which(INSTALL_SCRIPTS_DIR / pkg.file):
                yield cont(Path(s_path), bin=bin, pkg=pkg)


async def install() -> int:
    cols, _ = get_terminal_size()
    sep = cols * "="

    errors: MutableSequence[str] = []
    tasks = chain(_git(), _pip(), _gem(), _npm(), _go(), _script())
    for fut in chain(as_completed(tasks), (_binstub(),)):
        for debug, proc in await fut:
            args = join(map(str, proc.args))
            if proc.returncode == 0:
                msg = LANG("proc succeeded", args=args)
                print(
                    msg,
                    debug,
                    decode(proc.stderr),
                    decode(proc.stdout),
                    sep,
                    sep=linesep,
                )
            else:
                errors.append(args)
                msg = LANG("proc failed", code=proc.returncode, args=args)
                print(
                    msg,
                    debug,
                    decode(proc.stderr),
                    decode(proc.stdout),
                    sep,
                    sep=linesep,
                    file=stderr,
                )

    if errors:
        print(linesep.join(errors), file=stderr)

    return bool(errors)


async def maybe_install() -> None:
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
        ans = await Nvim.confirm(
            question=LANG("update?"),
            answers=LANG("ask yes/no"),
            answer_key={1: 1, 2: 2},
        )
        if ans:
            coded = str(now)
            UPDATE_LOG.write_text(coded)

        if ans == 1:
            await open_term(
                Path(executable).resolve(strict=True),
                INSTALL_SCRIPT,
                "deps",
                "packages",
            )
