from asyncio.tasks import as_completed
from datetime import datetime, timezone
from itertools import chain
from os import environ, pathsep, uname
from shutil import get_terminal_size, rmtree, which
from sys import stderr
from typing import Awaitable, Iterator, Sequence, Tuple

from pynvim.api.nvim import Nvim
from std2.asyncio.subprocess import ProcReturn, call
from std2.pickle import DecodeError, decode, encode
from std2.pickle.coders import datetime_str_decoder, datetime_str_encoder

from ..config.fmt import fmt_specs
from ..config.install import ScriptSpec
from ..config.linter import linter_specs
from ..config.lsp import lsp_specs
from ..config.pkgs import GitPkgSpec, pkg_specs
from ..config.tools import tool_specs
from ..consts import (
    BIN_DIR,
    GO_DIR,
    INSTALL_BIN_DIR,
    INSTALL_SCRIPT,
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
    return bool(
        which(script_spec.interpreter)
        and all(map(which, script_spec.required))
        and script_spec.body
    )


SortOfMonoid = Sequence[Tuple[str, ProcReturn]]


def _git() -> Iterator[Awaitable[SortOfMonoid]]:
    VIM_DIR.mkdir(parents=True, exist_ok=True)
    cmd = "git"

    if which(cmd):
        for spec in pkg_specs:

            async def cont(spec: GitPkgSpec) -> SortOfMonoid:
                location = VIM_DIR / p_name(spec.uri)
                if location.is_dir():
                    p1 = await call(cmd, "pull", "--recurse-submodules", cwd=location)
                else:
                    p1 = await call(
                        cmd,
                        "clone",
                        "--depth=1",
                        "--recurse-submodules",
                        "--shallow-submodules",
                        spec.uri,
                        str(location),
                    )

                pkg = spec.script
                if not p1.code and _installable(pkg):
                    stdin = pkg.body.encode()
                    p2 = await call(
                        pkg.interpreter,
                        stdin=stdin,
                        env=pkg.env,
                        cwd=location,
                    )
                    return (spec.uri, p1), (pkg.body, p2)
                else:
                    return ((spec.uri, p1),)

            yield cont(spec.git)


def _pip() -> Iterator[Awaitable[SortOfMonoid]]:
    PIP_DIR.mkdir(parents=True, exist_ok=True)
    cmd = "pip3"
    specs = tuple(_pip_specs())

    if which(cmd) and specs:

        async def cont() -> SortOfMonoid:
            p = await call(
                cmd,
                "install",
                "--upgrade",
                "--target",
                str(PIP_DIR),
                "--",
                *specs,
                cwd=PIP_DIR,
            )
            return (("", p),)

        yield cont()


def _npm() -> Iterator[Awaitable[SortOfMonoid]]:
    NPM_DIR.mkdir(parents=True, exist_ok=True)
    cmd = "npm"

    if which(cmd):

        async def cont() -> SortOfMonoid:
            p1 = await call(cmd, "init", "--yes", cwd=NPM_DIR)
            if p1.code:
                return (("", p1),)
            else:
                p2 = await call(
                    cmd, "install", "--upgrade", "--", *_npm_specs(), cwd=NPM_DIR
                )
                return ("", p1), ("", p2)

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
            )
            return (("", p),)

        yield cont()


def _script() -> Iterator[Awaitable[SortOfMonoid]]:
    if TMP_DIR.exists():
        rmtree(TMP_DIR)

    for path in (BIN_DIR, LIB_DIR, TMP_DIR):
        path.mkdir(parents=True, exist_ok=True)

    sys = uname()
    for bin, pkg in _script_specs():

        async def cont(bin: str, pkg: ScriptSpec) -> SortOfMonoid:
            env = {
                "PATH": pathsep.join((INSTALL_BIN_DIR, environ["PATH"])),
                "ARCH": sys.machine,
                "OS": sys.sysname,
                "BIN_NAME": bin,
                "BIN_PATH": str(BIN_DIR / bin),
                "LIB_PATH": str(LIB_DIR / bin),
                "TMP_DIR": str(TMP_DIR),
            }
            stdin = pkg.body.encode()
            p = await call(
                pkg.interpreter,
                stdin=stdin,
                env={**env, **pkg.env},
                cwd=VARS_DIR,
            )
            return ((pkg.body, p),)

        if _installable(pkg):
            yield cont(bin, pkg)


async def install() -> int:
    has_error = False
    for fut in as_completed(chain(_git(), _pip(), _npm(), _go(), _script())):
        for debug, proc in await fut:
            cols, _ = get_terminal_size((80, 40))
            sep = cols * "="
            args = " ".join(chain((proc.prog,), proc.args))
            if proc.code == 0:
                msg = LANG("proc succeeded", args=args)
                print(msg)
                print(debug)
                print(proc.out.decode())
                print(sep)
            else:
                has_error = True
                msg = LANG("proc failed", code=proc.code, args=args)
                print(msg, file=stderr)
                print(debug, file=stderr)
                print(proc.err, file=stderr)
                print(sep, file=stderr)

    return has_error


def maybe_install(nvim: Nvim) -> None:
    UPDATE_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        coded = UPDATE_LOG.read_text()
        before: datetime = decode(datetime, coded, decoders=(datetime_str_decoder,))
    except (FileNotFoundError, DecodeError):
        before = datetime(year=1949, month=9, day=21, tzinfo=timezone.utc)

    now = datetime.now(tz=timezone.utc)
    diff = now - before
    if diff.days > 7:
        ans = nvim.funcs.confirm(LANG("update?"), LANG("ask yes/no"), 2)
        if ans in {1, 2}:
            coded = encode(now, encoders=(datetime_str_encoder,))
            UPDATE_LOG.write_text(coded)

        if ans == 1:
            open_term(nvim, "python3", INSTALL_SCRIPT, "--install-packages")
