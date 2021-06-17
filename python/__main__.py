from argparse import ArgumentParser, Namespace
from asyncio import run as arun
from subprocess import check_call
from sys import executable, stderr
from typing import Literal, Sequence, Union
from venv import EnvBuilder

from .consts import REQUIREMENTS, RT_DIR, RT_PY, TOP_LEVEL

_LOCK_FILE = RT_DIR / "requirements.lock"


def parse_args() -> Namespace:
    parser = ArgumentParser()

    sub_parsers = parser.add_subparsers(dest="command", required=True)

    s_run = sub_parsers.add_parser("run")
    s_run.add_argument("--socket", required=True)

    s_deps = sub_parsers.add_parser("deps")
    s_deps.add_argument("deps", nargs="*", default=())

    return parser.parse_args()


args = parse_args()
command: Union[Literal["deps"], Literal["run"]] = args.command
req = REQUIREMENTS.read_bytes()

if command == "deps":
    deps: Sequence[str] = args.deps

    if not deps or "runtime" in deps:
        builder = EnvBuilder(
            system_site_packages=False,
            with_pip=True,
            upgrade=True,
            symlinks=True,
            clear=True,
        )
        builder.create(RT_DIR)
        check_call(
            (
                RT_PY,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--force-reinstall",
                "--requirement",
                str(REQUIREMENTS),
            )
        )

        _LOCK_FILE.write_bytes(req)

    if not deps or "packages" in deps:
        if executable != RT_PY:
            code = check_call(
                (RT_PY, "-m", "python", "deps", "packages"), cwd=TOP_LEVEL
            )
            exit(code)
        else:
            from .components.install import install

            code = arun(install())
            if code:
                exit(code)

elif command == "run":
    try:
        lock = _LOCK_FILE.read_bytes()
    except Exception:
        lock = b""

    assert executable == RT_PY
    assert lock == req

    from pynvim import attach
    from pynvim_pp.client import run_client
    from std2.pickle import DecodeError

    try:
        from .client import Client
    except DecodeError as e:
        print(e, file=stderr)
        exit(1)
    else:
        nvim = attach("socket", path=args.socket)
        code = run_client(nvim, client=Client())
        exit(code)

else:
    assert False

