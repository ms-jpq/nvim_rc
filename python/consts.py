from itertools import chain
from os import environ, pathsep
from pathlib import Path

DATE_FMT = "%Y-%m-%d %H:%M:%S"

TOP_LEVEL = Path(__file__).resolve().parent.parent

INSTALL_SCRIPT = str(TOP_LEVEL / "init.py")
REQUIREMENTS = str(TOP_LEVEL / "requirements.txt")
LANG_ROOT = TOP_LEVEL / "locale"
DEFAULT_LANG = "c"


CONF_DIR = TOP_LEVEL / "config"
CONF_PKGS = CONF_DIR / "packages.yml"
CONF_LSP = CONF_DIR / "lsp.yml"
CONF_LINT = CONF_DIR / "lint.yml"
CONF_FMT = CONF_DIR / "fmt.yml"


VARS_DIR = TOP_LEVEL / ".vars"
RT_DIR = VARS_DIR / "runtime"


BIN_DIR = VARS_DIR / "bin"
LIB_DIR = VARS_DIR / "lib"
_MODULES_DIR = VARS_DIR / "modules"
VIM_DIR = _MODULES_DIR / "vim_modules"
PIP_DIR = _MODULES_DIR / "pip_modules"
NPM_DIR = _MODULES_DIR
GO_DIR = _MODULES_DIR / "go_modules"

INSTALL_BIN_DIR = str(TOP_LEVEL / "python" / "components" / "bin")
PATH_PREPEND = tuple(
    map(
        str,
        (BIN_DIR, PIP_DIR / "bin", NPM_DIR / "node_modules" / ".bin", GO_DIR / "bin"),
    )
)
PATH = environ["PATH"] = pathsep.join(chain(PATH_PREPEND, (environ["PATH"],)))
PYTHONPATH = environ["PYTHONPATH"] = (
    pathsep.join((str(PIP_DIR), environ["PYTHONPATH"]))
    if "PYTHONPATH" in environ
    else str(PIP_DIR)
)


TMP_DIR = VARS_DIR / "tmp"


LOGS_DIR = VARS_DIR / "logs"
UPDATE_LOG = LOGS_DIR / "last_update.txt"


BACKUP_DIR = VARS_DIR / "backup"