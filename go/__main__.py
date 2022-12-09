from argparse import ArgumentParser, Namespace
from asyncio import run as arun
from contextlib import nullcontext
from pathlib import Path, PurePath
from subprocess import check_call
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

    with nullcontext(sub_parsers.add_parser("deps")) as p:
        p.add_argument("deps", nargs="*", default=())

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    command: Union[Literal["deps"], Literal["run"]] = args.command
    req = REQUIREMENTS.read_bytes()

    if command == "deps":
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
            check_call(
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
                )
            )

            _LOCK_FILE.write_bytes(req)

        if not deps or "packages" in deps:
            if _EX != RT_PY:
                code = check_call(
                    (
                        RT_PY,
                        "-m",
                        Path(__file__).resolve(strict=True).parent.name,
                        "deps",
                        "packages",
                    ),
                    cwd=TOP_LEVEL,
                )
                exit(code)
            else:
                from .components.install import install

                if code := arun(install()):
                    exit(code)

    elif command == "run":
        try:
            lock = _LOCK_FILE.read_bytes()
        except Exception:
            lock = b""

        assert _EX == RT_PY
        assert lock == req

        from std2.pickle.types import DecodeError

        try:
            from .client import init
        except DecodeError as e:
            print(e, file=stderr)
            exit(1)
        else:

            async def m() -> None:
                await init(args.socket, ppid= args.ppid)

            arun(m())

    else:
        assert False


if __name__ == "__main__":
    main()
