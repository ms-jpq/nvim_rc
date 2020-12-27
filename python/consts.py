from os import environ
from pathlib import Path

TOP_LEVEL = Path(__file__).resolve().parent.parent
SUB_MODULES = tuple((TOP_LEVEL / "submodules").iterdir())

XDG_DATA_HOME = environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")


CONF_DIR = TOP_LEVEL / "config"
CONF_PACKAGES = CONF_DIR / "packages.yml"


VARS_DIR = TOP_LEVEL / "vars"
VIM_DIR = VARS_DIR / "vim_modules"
PIP_DIR = VARS_DIR / "pip_modules"
NPM_DIR = VARS_DIR / "node_modules"

BINS = (TOP_LEVEL / "bin", PIP_DIR / "bin", NPM_DIR / ".bin")
