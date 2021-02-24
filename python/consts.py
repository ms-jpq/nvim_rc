from itertools import chain
from os import environ, pathsep
from pathlib import Path

DATE_FMT = "%Y-%m-%d %H:%M:%S"

TOP_LEVEL = Path(__file__).resolve().parent.parent

RT_DIR = TOP_LEVEL / ".vars" / "runtime"
RT_BIN = RT_DIR / "bin"
RT_PY = str(RT_BIN / "python3")


REQUIREMENTS = str(TOP_LEVEL / "requirements.txt")
INSTALL_SCRIPT = str(TOP_LEVEL / "init.py")

LANG_ROOT = TOP_LEVEL / "locale"
DEFAULT_LANG = "c"


CONF_DIR = TOP_LEVEL / "config"
CONF_PKGS = CONF_DIR / "packages.yml"
CONF_LSP = CONF_DIR / "lsp.yml"
CONF_LINT = CONF_DIR / "lint.yml"
CONF_FMT = CONF_DIR / "fmt.yml"
CONF_TOOL = CONF_DIR / "tools.yml"

VARS_DIR = TOP_LEVEL / ".vars"


BIN_DIR = VARS_DIR / "bin"
LIB_DIR = VARS_DIR / "lib"
_MODULES_DIR = VARS_DIR / "modules"
VIM_DIR = _MODULES_DIR / "vim_modules"
VENV_DIR = _MODULES_DIR / "py_modules"
NPM_DIR = _MODULES_DIR
GO_DIR = _MODULES_DIR / "go_modules"

INSTALL_BIN_DIR = str(TOP_LEVEL / "python" / "components" / "bin")
_PATH_PREPEND = tuple(
    map(
        str,
        (BIN_DIR, VENV_DIR / "bin", NPM_DIR / "node_modules" / ".bin", GO_DIR / "bin"),
    )
)
_PATHS = environ["PATH"] = pathsep.join(chain(_PATH_PREPEND, (environ["PATH"],)))
PATH = pathsep.join(path for path in _PATHS.split(pathsep) if path != str(RT_BIN))


TMP_DIR = VARS_DIR / "tmp"

LOGS_DIR = VARS_DIR / "logs"
UPDATE_LOG = LOGS_DIR / "last_update.txt"


BACKUP_DIR = VARS_DIR / "backup"
