from os import environ, pathsep
from pathlib import Path

XDG_DATA_HOME = environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")

TOP_LEVEL = Path(__file__).resolve().parent.parent


CONF_DIR = TOP_LEVEL / "config"
CONF_PKGS = CONF_DIR / "packages.yml"
CONF_LSP = CONF_DIR / "lsp.yml"
CONF_LINT = CONF_DIR / "lint.yml"
CONF_FMT = CONF_DIR / "fmt.yml"


VARS_DIR = TOP_LEVEL / "vars"
RT_DIR = str(VARS_DIR / "runtime")
VIM_DIR = VARS_DIR / "vim_modules"
PIP_DIR = VARS_DIR / "pip_modules"
NPM_DIR = VARS_DIR
BIN_PATHS = pathsep.join(
    map(str, (TOP_LEVEL / "bin", PIP_DIR / "bin", NPM_DIR / ".bin"))
)


INSTALL_PROG = str(TOP_LEVEL / "install.py")