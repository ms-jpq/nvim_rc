#!/usr/bin/env -S -- PYTHONSAFEPATH= python3

from argparse import ArgumentParser, Namespace
from contextlib import suppress
from datetime import timezone
from email.utils import parsedate_to_datetime
from http.client import HTTPResponse
from io import DEFAULT_BUFFER_SIZE
from os import utime
from pathlib import Path, PurePosixPath
from posixpath import normcase
from sys import stderr, stdout
from tempfile import NamedTemporaryFile
from textwrap import dedent
from typing import Iterator, Tuple, cast
from urllib.parse import unquote, urlsplit
from urllib.request import Request, build_opener

_OPEN = build_opener()


def _meta(uri: str, timeout: float) -> Tuple[int, float]:
    req = Request(url=uri, method="HEAD")
    with _OPEN.open(req, timeout=timeout) as resp:
        resp = cast(HTTPResponse, resp)
        tot, mtime = 0, 0.0
        for key, val in resp.headers.items():
            match = key.casefold()
            if match == "content-length":
                tot = int(val)
            elif match == "last-modified":
                if req_mtime := parsedate_to_datetime(val):
                    mtime = req_mtime.replace(tzinfo=timezone.utc).timestamp()

        return tot, mtime


def _fetch(uri: str, timeout: float) -> Iterator[bytes]:
    with _OPEN.open(uri, timeout=timeout) as resp:
        resp = cast(HTTPResponse, resp)
        while buf := resp.read(DEFAULT_BUFFER_SIZE):
            yield buf


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst", nargs="?", default=None)
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    src: str = args.src
    path = PurePosixPath(unquote(urlsplit(src).path))
    dst = Path(args.dst if args.dst else path.name).resolve(strict=False)

    msg = f"""
    {src}
    >>>
    {dst}
    """
    stderr.write(dedent(msg))

    size, mtime = _meta(src, timeout=args.timeout)
    with suppress(FileNotFoundError):
        stat = dst.stat()
        if size == stat.st_size and mtime == stat.st_mtime:
            stdout.write(normcase(dst))
            return

    stream = _fetch(src, timeout=args.timeout)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=dst.parent, prefix=dst.name, delete=False) as fd:
        fd.writelines(stream)

    Path(fd.name).replace(dst)
    utime(dst, (mtime, mtime))
    stdout.write(normcase(dst))


main()