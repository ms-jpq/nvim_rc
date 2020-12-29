#!/usr/bin/env python3

from subprocess import run
from pathlib import Path

WD = Path(__file__).resolve().parent
RUNTIME = str(WD / "vars" / "runtime")
REQUIREMENTS = str(WD / "requirements.txt")


proc = run(
    (
        "pip3",
        "install",
        "--upgrade",
        "--target",
        RUNTIME,
        "--requirement",
        REQUIREMENTS,
    )
)
exit(proc.returncode)
