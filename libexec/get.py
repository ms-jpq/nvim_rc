#!/usr/bin/env -S -- PYTHONSAFEPATH= python3

from argparse import ArgumentParser, Namespace
from contextlib import suppress
from pathlib import Path, PurePosixPath
from posixpath import normcase
from shlex import join
from shutil import which
from subprocess import check_call
from sys import stderr, stdout
from textwrap import dedent
from urllib.parse import unquote, urlsplit


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst", nargs="?", default=None)
    parser.add_argument("--timeout", type=float, default=600.0)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    src = str(args.src)
    path = PurePosixPath(unquote(urlsplit(src).path))
    dst = Path(args.dst if args.dst else path.name).resolve(strict=False)

    etag = dst.with_name(f"{dst.name}.etag")
    ttag = dst.with_name(f"{dst.name}.ttag")
    tmp = dst.with_name(f"{dst.name}.tmp")

    curl = which("curl")
    assert curl
    argv = (
        curl,
        "--fail",
        "--location",
        "--remote-time",
        "--no-progress-meter",
        "--max-time",
        str(args.timeout),
        "--etag-compare",
        etag,
        "--etag-save",
        ttag,
        "--output",
        tmp,
        "--",
        src,
    )

    msg = f"""
    {src}
    >>>
    {dst}
    """

    stderr.write(dedent(msg))
    stderr.write(join(map(str, argv)))

    if not dst.is_file():
        etag.unlink(missing_ok=True)

    try:
        check_call(argv, stdout=stderr.fileno())
        with suppress(FileNotFoundError):
            tmp.rename(dst)
        with suppress(FileNotFoundError):
            ttag.rename(etag)
    finally:
        tmp.unlink(missing_ok=True)
        ttag.unlink(missing_ok=True)

    stdout.write(normcase(dst))


main()
