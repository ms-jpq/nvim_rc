from asyncio import create_task
from asyncio.tasks import as_completed, wait
from fnmatch import fnmatch
from itertools import chain, repeat
from json import dumps
from multiprocessing import cpu_count
from os import PathLike, environ, extsep, linesep, pathsep, sep
from os.path import normcase
from pathlib import Path, PurePath
from shlex import join
from shutil import get_terminal_size
from subprocess import CompletedProcess
from sys import executable, stderr, stdout
from tempfile import TemporaryDirectory
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
    Union,
)
from venv import EnvBuilder

from pynvim_pp.lib import encode
from pynvim_pp.nvim import Nvim
from std2.asyncio.subprocess import call
from std2.pathlib import AnyPath
from std2.platform import OS, os

from ..config.fmt import fmt_specs
from ..config.install import ScriptSpec, which
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import PkgAttrs, pkg_specs
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


_GEMS = GEM_DIR / "gems"


def _pip_specs() -> Iterator[str]:
    values = chain(lsp_specs().values(), linter_specs().values(), fmt_specs().values())
    for spec in values:
        if all(map(which, spec.install.requires)):
            yield from spec.install.pip
    yield from tool_specs().pip


def _gem_specs() -> Iterator[str]:
    values = chain(lsp_specs().values(), linter_specs().values(), fmt_specs().values())
    for spec in values:
        if all(map(which, spec.install.requires)):
            yield from spec.install.gem
    yield from tool_specs().gem


def _npm_specs() -> Iterator[str]:
    values = chain(lsp_specs().values(), linter_specs().values(), fmt_specs().values())
    for spec in values:
        if all(map(which, spec.install.requires)):
            yield from spec.install.npm
    yield from tool_specs().npm


def _script_specs() -> Iterator[Tuple[PurePath, ScriptSpec]]:
    values = chain(lsp_specs().values(), linter_specs().values(), fmt_specs().values())
    for spec in values:
        if all(map(which, spec.install.requires)):
            yield spec.bin, spec.install.script
    for t_spec in tool_specs().script:
        if file := t_spec.file:
            yield PurePath(file.stem), t_spec


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

        async def cont(
            location: Path,
            uri: str,
            spec: PkgAttrs,
        ) -> _SortOfMonoid:
            async def cont() -> AsyncIterator[Tuple[str, CompletedProcess[bytes]]]:
                assert git
                jobs = f"--jobs={cpu_count()}"
                if location.is_dir():
                    p1 = await _run(
                        git,
                        "-C",
                        location,
                        "pull",
                        "--recurse-submodules",
                        "--no-tags",
                        jobs,
                        "--force",
                        "--quiet",
                        *(("origin", spec.branch) if spec.branch else ()),
                    )
                else:
                    p1 = await _run(
                        git,
                        "clone",
                        "--config",
                        "core.symlinks=true",
                        "--recurse-submodules",
                        "--shallow-submodules",
                        "--depth=1",
                        jobs,
                        *(("--branch", spec.branch) if spec.branch else ()),
                        "--quiet",
                        "--",
                        uri,
                        location,
                    )
                yield uri, p1

                if not p1.returncode:
                    for call in spec.call:
                        arg0, *argv = call
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
                            if p2.returncode:
                                break

            return [rt async for rt in cont()]

        for uri, spec in pkg_specs().items():
            if not mvp or spec.mvp:
                location = p_name(spec.opt, uri=uri)
                if _match(match, name=location.name):
                    yield cont(location, uri=uri, spec=spec)


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
                "--quiet",
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
        and (
            specs := {
                *(
                    spec
                    for spec in _gem_specs()
                    if _match(match, name=name) or _match(match, name=spec)
                )
            }
        )
        and (os != OS.macos or not gem.is_relative_to(PurePath(sep) / "usr" / "bin"))
        and os != OS.windows
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
                json = {"devDependencies": {key: "*" for key in specs}}
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
                yield "", p2

            return [rt async for rt in cont()]

        yield cont()


def _script(match: AbstractSet[str]) -> Iterator[Awaitable[_SortOfMonoid]]:
    libexec = normcase(LIBEXEC)
    for path in (BIN_DIR, LIB_DIR, TMP_DIR):
        path.mkdir(parents=True, exist_ok=True)

    for bin, pkg in _script_specs():

        async def cont(path: Path, bin: PurePath) -> _SortOfMonoid:
            with TemporaryDirectory(dir=TMP_DIR, prefix=path.name + extsep) as tmp:
                env = {
                    "PATH": pathsep.join((libexec, environ["PATH"])),
                    "BIN": normcase(BIN_DIR / bin),
                    "LIB": normcase(LIB_DIR / bin),
                    "LIBEXEC": libexec,
                    "TMP": tmp,
                }

                if tramp := which("env"):
                    argv: Sequence[AnyPath] = (tramp, "--", path)
                else:
                    argv = (path,)

                p = await _run(
                    *argv,
                    env=env,
                    cwd=TMP_DIR,
                )
                return (("", p),)

        if (
            pkg.file
            and (s_path := which(DLEXEC / pkg.file))
            and _match(match, name=pkg.file.name)
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
    UPDATE_LOG.parent.mkdir(parents=True, exist_ok=True)
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
