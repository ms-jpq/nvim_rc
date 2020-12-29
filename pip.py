#!/usr/bin/env python3

from subprocess import run
from pathlib import Path
from python.consts import RT_DIR


REQUIREMENTS = str(Path(__file__).resolve().parent / "requirements.txt")


proc = run(
    (
        "pip3",
        "install",
        "--upgrade",
        "--target",
        RT_DIR,
        "--requirement",
        REQUIREMENTS,
    ),
    cwd=RT_DIR,
)
exit(proc.returncode)
