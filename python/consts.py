from os import environ
from pathlib import Path

TOP_LEVEL = Path(__file__).resolve().parent.parent
SUB_MODULES = tuple((TOP_LEVEL / "submodules").iterdir())

XDG_DATA_HOME = environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
CONF_DIR = TOP_LEVEL / "config"
_VARS_DIR = TOP_LEVEL / "vars"
GIT_DIR = _VARS_DIR / "vim"
PIP_DIR = _VARS_DIR / "pip"
NPM_DIR = _VARS_DIR / "npm"