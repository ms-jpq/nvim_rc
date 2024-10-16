import sys
from argparse import ArgumentParser, Namespace
from asyncio import run as arun
from contextlib import nullcontext, suppress
from os import chdir, environ
from pathlib import Path, PurePath
from subprocess import run
from sys import executable, exit, stderr
from typing import Literal, Sequence, Tuple, Union
from venv import EnvBuilder

from .consts import IS_WIN, REQUIREMENTS, RT_DIR, RT_PY, TOP_LEVEL

_EX = Path(executable)
_EX = _EX.parent.resolve(strict=True) / _EX.name
_LOCK_FILE = RT_DIR / "requirements.lock"


def _socket(arg: str) -> Union[PurePath, Tuple[str, int]]:
    if arg.startswith("localhost:"):
        host, _, port = arg.rpartition(":")
        return host, int(port)
    else:
        return PurePath(arg)


def _parse_args() -> Namespace:
    parser = ArgumentParser()

    sub_parsers = parser.add_subparsers(dest="command", required=True)

    with nullcontext(sub_parsers.add_parser("run")) as p:
        p.add_argument("--ppid", type=int)
        p.add_argument("--socket", required=True, type=_socket)
        p.add_argument("--cwd", required=True, type=PurePath)

    with nullcontext(sub_parsers.add_parser("deps")) as p:
        p.add_argument("deps", nargs="*", default=())

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    command: Union[Literal["deps"], Literal["run"]] = args.command
    req = REQUIREMENTS.read_bytes()

    if command == "deps":
        if sys.platform == "win32":
            from subprocess import BELOW_NORMAL_PRIORITY_CLASS

            nice = lambda _: None
        else:
            from os import nice

            BELOW_NORMAL_PRIORITY_CLASS = 0

        with suppress(PermissionError):
            nice(19)

        deps: Sequence[str] = args.deps

        if not deps or "runtime" in deps:
            builder = EnvBuilder(
                system_site_packages=False,
                with_pip=True,
                upgrade=True,
                symlinks=not IS_WIN,
                clear=True,
            )
            builder.create(RT_DIR)
            proc = run(
                (
                    RT_PY,
                    "-m",
                    "pip",
                    "install",
                    "--require-virtualenv",
                    "--upgrade",
                    "--force-reinstall",
                    "--requirement",
                    REQUIREMENTS,
                ),
                creationflags=BELOW_NORMAL_PRIORITY_CLASS,
            )

            if proc.returncode:
                exit(proc.returncode)

            _LOCK_FILE.write_bytes(req)

        if not deps or "packages" in deps:
            if _EX != RT_PY:
                proc = run(
                    (
                        RT_PY,
                        "-m",
                        Path(__file__).resolve(strict=True).parent.name,
                        "deps",
                        *({*deps, "packages"} - {"runtime"}),
                    ),
                    cwd=TOP_LEVEL,
                    creationflags=BELOW_NORMAL_PRIORITY_CLASS,
                )
                exit(proc.returncode)
            else:
                from .components.install import install

                match = {p} if (p := environ.get("PKG")) else set()
                if code := arun(install("mvp" in deps, match=match)):
                    exit(code)

    elif command == "run":
        try:
            lock = _LOCK_FILE.read_bytes()
        except Exception:
            lock = b""

        assert _EX == RT_PY
        assert lock == req

        from std2.pickle.types import DecodeError

        chdir(args.cwd)
        try:
            from .client import init
        except DecodeError as e:
            print(e, file=stderr)
            exit(1)
        else:
            arun(init(args.socket, ppid=args.ppid))

    else:
        assert False


if __name__ == "__main__":
    main()
