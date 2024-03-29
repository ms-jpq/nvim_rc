#!/usr/bin/env -S -- PYTHONSAFEPATH= python3

from argparse import ArgumentParser, Namespace
from pathlib import Path, PurePath
from shutil import register_unpack_format, unpack_archive, which
from subprocess import check_call
from sys import stderr, stdin
from textwrap import dedent

_STDIN = PurePath("-")


def _unpack_gz(source: str, destination: str) -> None:
    cmd = "gzip"
    if gzip := which(cmd):
        dst = Path(destination) / PurePath(source).name
        with dst.open("wb") as fd:
            check_call(
                (gzip, "--decompress", "--keep", "--force", "--stdout", "--", source),
                stdout=fd,
            )
    else:
        raise RuntimeError(f"No '{cmd}' found in $PATH")


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("src", nargs="?", type=Path, default=_STDIN)
    parser.add_argument("-f", "--format")
    parser.add_argument("-d", "--dst", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> None:
    register_unpack_format("gz", extensions=[".gz"], function=_unpack_gz)
    args = _parse_args()

    src = stdin.read() if args.src == _STDIN else args.src
    msg = f"""
    {src}
    -> -> ->
    {args.dst}
    """

    unpack_archive(src, format=args.format, extract_dir=args.dst)
    stderr.write(dedent(msg))


main()
