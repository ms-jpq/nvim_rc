#!/usr/bin/env python3

from subprocess import run
from pathlib import Path

WD = Path(__file__).resolve().parent
PIP_HOME = str(WD / "vars" / "requirements")
REQUIREMENTS = str(WD / "requirements.txt")


proc = run(
    (
        "pip3",
        "install",
        "--upgrade",
        "--target",
        PIP_HOME,
        "--requirement",
        REQUIREMENTS,
    )
)
exit(proc.returncode)
