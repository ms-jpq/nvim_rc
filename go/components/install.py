from asyncio import create_task
from asyncio.tasks import as_completed, wait
from fnmatch import fnmatch
from itertools import chain, repeat
from json import dumps, loads
from multiprocessing import cpu_count
from os import PathLike, environ, linesep, pathsep, sep
from os.path import normcase
from pathlib import Path, PurePath
from shlex import join, split
from shutil import get_terminal_size, which
from subprocess import CompletedProcess
from sys import executable, stderr, stdout
from time import time
from typing import (
    AbstractSet,
    Any,
    AsyncIterator,
    Awaitable,
    Iterator,
    Mapping,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    Union,
)
from venv import EnvBuilder

from pynvim_pp.lib import decode, encode
from pynvim_pp.nvim import Nvim
from std2.asyncio.subprocess import call
from std2.pathlib import AnyPath
from std2.platform import OS, os

from ..config.fmt import fmt_specs
from ..config.install import ScriptSpec
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import GitPkgSpec, pkg_specs
from ..config.tools import tool_specs
from ..consts import (
    BIN_DIR,
    DEADLINE,
    DLEXEC,
    GEM_DIR,
    INSTALL_SCRIPT,
    LIB_DIR,
    LIBEXEC,
    NPM_DIR,
    PIP_DIR,
    RT_SCRIPTS,
    TMP_DIR,
    UPDATE_LOG,
    VIM_DIR,
)
from ..registry import LANG
from ..workspace.terminal import open_term
from .rtp import p_name

_SortOfMonoid = Sequence[Tuple[str, CompletedProcess[bytes]]]


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


def _script_specs() -> Iterator[Tuple[str, ScriptSpec]]:
    for l_spec in lsp_specs:
        yield l_spec.bin, l_spec.install.script
    for i_spec in linter_specs:
        yield i_spec.bin, i_spec.install.script
    for f_spec in fmt_specs:
        yield f_spec.bin, f_spec.install.script
    for t_spec in tool_specs.script:
        if file := t_spec.file:
            yield file.stem, t_spec


def _match(match: AbstractSet[str], name: str) -> bool:
    return not match or any(fnmatch(name, m) for m in match)


async def _run(
    *argv: Union[str, PathLike[Any]],
    env: Optional[Mapping[str, str]] = None,
    cwd: Optional[PurePath] = None,
) -> CompletedProcess[bytes]:
    p = call(
        *argv,
        env=env,
        cwd=cwd,
        check_returncode=set(),
    )
    t = create_task(p)
    done, _ = await wait((t,), timeout=DEADLINE)
    if done:
        try:
            return await t
        except OSError as e:
            raise RuntimeError(argv) from e
    else:
        raise TimeoutError(argv)


def _git(mvp: bool, match: AbstractSet[str]) -> Iterator[Awaitable[_SortOfMonoid]]:
    for dir in ("start", "opt"):
        (VIM_DIR / dir).mkdir(parents=True, exist_ok=True)

    if git := which("git"):

        async def cont(spec: GitPkgSpec, location: Path) -> _SortOfMonoid:
            async def cont() -> AsyncIterator[Tuple[str, CompletedProcess[bytes]]]:
                assert git
                jobs = f"--jobs={cpu_count()}"
                if location.is_dir():
                    p1 = await _run(
                        git,
                        "pull",
                        "--recurse-submodules",
                        "--no-tags",
                        jobs,
                        "--force",
                        *(("origin", spec.branch) if spec.branch else ()),
                        cwd=location,
                    )
                else:
                    p1 = await _run(
                        git,
                        "clone",
                        "--recurse-submodules",
                        "--shallow-submodules",
                        "--depth=1",
                        jobs,
                        *(("--branch", spec.branch) if spec.branch else ()),
                        "--",
                        spec.uri,
                        location,
                    )
                yield spec.uri, p1

                if not p1.returncode and spec.call:
                    arg0, *argv = spec.call
                    a00 = (
                        Path(executable).resolve(strict=True)
                        if arg0 in {"python", "python3"}
                        else Path(arg0)
                    )
                    if a0 := which(a00):
                        p2 = await _run(
                            a0,
                            *argv,
                            cwd=location,
                        )
                        yield "", p2

            return [rt async for rt in cont()]

        for spec in pkg_specs:
            if not mvp or spec.git.mvp:
                location = p_name(spec.opt, uri=spec.git.uri)
                if _match(match, name=location.name):
                    yield cont(spec.git, location=location)


def _pip(match: AbstractSet[str]) -> Iterator[Awaitable[_SortOfMonoid]]:
    name = "pip"
    if specs := {
        *(
            spec
            for spec in _pip_specs()
            if _match(match, name=name) or _match(match, name=spec)
        )
    }:
        builder = EnvBuilder(
            system_site_packages=False,
            with_pip=True,
            upgrade=True,
            symlinks=os is not OS.windows,
            clear=False,
        )
        builder.create(PIP_DIR)
        ex = PIP_DIR / RT_SCRIPTS / PurePath(executable).name

        async def cont() -> _SortOfMonoid:
            p = await _run(
                ex,
                "-m",
                name,
                "install",
                "--require-virtualenv",
                "--upgrade",
                "--",
                *specs,
            )
            return (("", p),)

        yield cont()


def _gem(match: AbstractSet[str]) -> Iterator[Awaitable[_SortOfMonoid]]:
    name = "gem"
    if (
        (gem := which(name))
        and (os != OS.macos or gem != "/usr/bin/gem")
        and (
            specs := {
                *(
                    spec
                    for spec in _gem_specs()
                    if _match(match, name=name) or _match(match, name=spec)
                )
            }
        )
        and (
            os != OS.macos
            or not PurePath(gem).is_relative_to(PurePath(sep) / "usr" / "bin")
        )
    ):

        async def cont() -> _SortOfMonoid:
            async def cont() -> AsyncIterator[Tuple[str, CompletedProcess[bytes]]]:
                assert gem
                p1 = await _run(
                    gem,
                    "install",
                    "--install-dir",
                    _GEMS,
                    "--no-document",
                    *specs,
                )
                yield ("", p1)
                if not p1.returncode:
                    p2 = await _run(
                        executable,
                        LIBEXEC / "binstub.py",
                        "--src",
                        _GEMS,
                        "--dst",
                        GEM_DIR / "bin",
                    )
                    yield ("", p2)

            return [rt async for rt in cont()]

        yield cont()


def _npm(match: AbstractSet[str]) -> Iterator[Awaitable[_SortOfMonoid]]:
    NPM_DIR.mkdir(parents=True, exist_ok=True)
    packages_json = NPM_DIR / "package.json"
    package_lock = NPM_DIR / "package-lock.json"
    name = "npm"

    if (
        which("node")
        and (npm := which(name))
        and (specs := ({*(_npm_specs())} if _match(match, name=name) else ()))
    ):

        async def cont() -> _SortOfMonoid:
            async def cont() -> AsyncIterator[Tuple[str, CompletedProcess[bytes]]]:
                assert npm
                packages_json.unlink(missing_ok=True)

                p1 = await _run(
                    npm,
                    "init",
                    "--yes",
                    cwd=NPM_DIR,
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

                    p2 = await _run(
                        npm,
                        "install",
                        "--no-package-lock",
                        "--upgrade",
                        cwd=NPM_DIR,
                    )
                    yield ("", p2)

            return [rt async for rt in cont()]

        yield cont()


def _script(match: AbstractSet[str]) -> Iterator[Awaitable[_SortOfMonoid]]:
    libexec = normcase(LIBEXEC)
    for path in (BIN_DIR, LIB_DIR, TMP_DIR):
        path.mkdir(parents=True, exist_ok=True)

    for bin, pkg in _script_specs():

        async def cont(path: Path, bin: str) -> _SortOfMonoid:
            env = {
                "PATH": pathsep.join((libexec, environ["PATH"])),
                "PYTHON": executable,
                "BIN": normcase(BIN_DIR / bin),
                "LIB": normcase(LIB_DIR / bin),
                "LIBEXEC": libexec,
            }

            if os is OS.windows and (tramp := which("env")):
                shebang = b"#!/usr/bin/env "
                with path.open("rb") as f:
                    if f.read(len(shebang)) == shebang:
                        args = split(decode(next(f, b"")))
                        argv: Sequence[AnyPath] = (tramp, *args, path)
                    else:
                        argv = (path,)
            else:
                argv = (path,)

            p = await _run(
                *argv,
                env=env,
                cwd=TMP_DIR,
            )
            return (("", p),)

        if pkg.file and all(map(which, pkg.required)):
            if (s_path := which(DLEXEC / pkg.file)) and _match(
                match, name=pkg.file.name
            ):
                yield cont(Path(s_path), bin=bin)


async def install(mvp: bool, match: AbstractSet[str]) -> int:
    cols, _ = get_terminal_size()
    sep = cols * b"="
    l = encode(linesep)
    ls = repeat(l)

    errors: MutableSequence[bytes] = []
    tasks = (
        chain(_git(mvp, match=match))
        if mvp
        else chain(
            _git(mvp, match=match),
            _pip(match),
            _gem(match),
            _npm(match),
            _script(match),
        )
    )
    for fut in as_completed(tasks):
        for debug, proc in await fut:
            args = join(map(str, proc.args))
            if proc.returncode == 0:
                msg = LANG("proc succeeded", args=args)
                lines = chain.from_iterable(
                    zip((encode(msg), encode(debug), proc.stderr, proc.stdout, sep), ls)
                )
                stdout.buffer.writelines(lines)
                stdout.buffer.flush()
            else:
                errors.append(b"!!! -- " + encode(args))
                msg = LANG("proc failed", code=proc.returncode, args=args)
                lines = chain.from_iterable(
                    zip((encode(msg), encode(debug), proc.stderr, proc.stdout, sep), ls)
                )
                stderr.buffer.writelines(lines)
                stderr.buffer.flush()

    if errors:
        stderr.buffer.write(l.join(errors))
    else:
        UPDATE_LOG.parent.mkdir(parents=True, exist_ok=True)
        UPDATE_LOG.write_text(str(time()))

    return bool(errors)


async def maybe_install() -> None:
    try:
        coded = UPDATE_LOG.read_text()
    except FileNotFoundError:
        before = 0.0
    else:
        before = float(coded)

    diff = time() - before
    if diff > (7 * 24 * 3600):
        ans = await Nvim.confirm(
            question=LANG("update?"),
            answers=LANG("ask yes/no"),
            answer_key={1: 1, 2: 2},
        )
        if ans:
            UPDATE_LOG.write_text(str(time()))

        if ans == 1:
            await open_term(INSTALL_SCRIPT, "packages")
