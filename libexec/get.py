#!/usr/bin/env -S -- PYTHONSAFEPATH= python3

from argparse import ArgumentParser, Namespace
from collections.abc import Iterator
from pathlib import Path, PurePath, PurePosixPath
from posixpath import normcase
from shutil import which
from subprocess import check_call
from sys import stderr, stdout
from textwrap import dedent
from typing import Union
from urllib.parse import unquote, urlsplit


def _curl(
    etag: PurePath, src: str, ttag: PurePath, tmp: PurePath, timeout: float
) -> Iterator[Union[PurePath, str]]:
    curl = which("curl")
    assert curl
    yield curl
    yield from ("--fail", "--location", "--remote-time", "--no-progress-meter")
    yield "--max-time"
    yield str(timeout)
    yield "--etag-compare"
    yield etag
    yield "--etag-save"
    yield ttag
    yield "--output"
    yield tmp
    yield "--"
    yield src


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst", nargs="?", default=None)
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    src = str(args.src)
    path = PurePosixPath(unquote(urlsplit(src).path))
    dst = Path(args.dst if args.dst else path.name).resolve(strict=False)

    etag = dst.with_name(f"{dst.name}.etag")
    ttag = dst.with_name(f"{dst.name}.ttag")
    tmp = dst.with_name(f"{dst.name}.tmp")
    curl = tuple(_curl(etag, src=src, ttag=ttag, tmp=tmp, timeout=args.timeout))

    msg = f"""
    {src}
    >>>
    {dst}
    """
    stderr.write(dedent(msg))

    try:
        check_call(curl)
        tmp.rename(dst)
        ttag.rename(etag)
    finally:
        tmp.unlink(missing_ok=True)
        ttag.unlink(missing_ok=True)

    stdout.write(normcase(dst))


main()
