#!/usr/bin/env -S -- PYTHONSAFEPATH= python3

from argparse import ArgumentParser, Namespace
from os import linesep, name
from os.path import commonpath, normcase
from pathlib import Path
from shlex import quote
from stat import S_IRGRP, S_IROTH, S_IRUSR, S_IWUSR, S_IXGRP, S_IXOTH, S_IXUSR
from string import Template
from sys import stderr
from tempfile import NamedTemporaryFile

_RWXR_XR_X = (S_IRUSR | S_IWUSR | S_IXUSR) | (S_IRGRP | S_IXGRP) | (S_IROTH | S_IXOTH)


_STUB = """
#!/usr/bin/env -S -- sh

export -- MSYSTEM='MSYS' GEM_PATH=$GEM_PATH
exec $BIN "$$@"
"""


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--src", type=Path)
    parser.add_argument("--dst", type=Path)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    src, dst = Path(args.src), Path(args.dst)
    template = Template(_STUB.lstrip())
    bins = src / "bin"
    win = name == "nt"
    tmp = Path(__file__).parent.parent.parent / "var" / "tmp"

    for path in (bins, dst):
        path.mkdir(parents=True, exist_ok=True)

    for path in bins.iterdir():
        bin = dst / path.name
        stub = template.substitute(
            GEM_PATH=quote(normcase(src)),
            BIN=quote(normcase(path)),
        )
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=tmp, delete=False
        ) as fd:
            fd.write(stub)

        Path(fd.name).replace(bin)
        bin.chmod(_RWXR_XR_X)

        if win:
            sh = bin.with_suffix(".sh")
            sh.unlink(missing_ok=True)
            sh.symlink_to(bin)

        common = commonpath((path, bin))
        for m in map(
            str, (path.relative_to(common), " -> ", bin.relative_to(common), linesep)
        ):
            stderr.write(m)


main()
