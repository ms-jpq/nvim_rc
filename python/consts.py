from pathlib import Path

TOP_LEVEL = Path(__file__).resolve().parent.parent


CONF_DIR = TOP_LEVEL / "config"
CONF_PKGS = CONF_DIR / "packages.yml"
CONF_LSP = CONF_DIR / "lsp.yml"
CONF_LINT = CONF_DIR / "lint.yml"
CONF_FMT = CONF_DIR / "fmt.yml"


_VARS_DIR = TOP_LEVEL / ".vars"
RT_DIR = str(_VARS_DIR / "runtime")

_MODULES_DIR = _VARS_DIR / "modules"
VIM_DIR = _MODULES_DIR / "vim_modules"
PIP_DIR = _MODULES_DIR / "pip_modules"
NPM_DIR = _MODULES_DIR
PATH_PREPEND = tuple(
    map(str, (TOP_LEVEL / "bin", PIP_DIR / "bin", NPM_DIR / "node_modules" / ".bin"))
)

LOGS_DIR = _VARS_DIR / "logs"
UPDATE_LOG = LOGS_DIR / "last_update.txt"

INSTALL_PROG = str(TOP_LEVEL / "install.py")

BACKUP_DIR = str(_VARS_DIR / "backup")
