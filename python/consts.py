from os import environ
from pathlib import Path

TOP_LEVEL = Path(__file__).resolve().parent.parent
SUB_MODULES = tuple((TOP_LEVEL / "submodules").iterdir())

XDG_DATA_HOME = environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
