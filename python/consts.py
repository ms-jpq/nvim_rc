from itertools import chain
from os import environ, pathsep
from os.path import normcase
from pathlib import Path, PurePath

DATE_FMT = "%Y-%m-%d %H:%M:%S"

TOP_LEVEL = Path(__file__).resolve().parent.parent

RT_DIR = TOP_LEVEL / ".vars" / "runtime"
RT_BIN = RT_DIR / "bin"
RT_PY = RT_BIN / "python3"


REQUIREMENTS = TOP_LEVEL / "requirements.txt"
INSTALL_SCRIPT = TOP_LEVEL / "init.py"

LANG_ROOT = TOP_LEVEL / "locale"
DEFAULT_LANG = "c"


CONF_DIR = TOP_LEVEL / "config"
CONF_PKGS = CONF_DIR / "packages.yml"
CONF_LSP = CONF_DIR / "lsp.yml"
CONF_LINT = CONF_DIR / "lint.yml"
CONF_FMT = CONF_DIR / "fmt.yml"
CONF_TOOL = CONF_DIR / "tools.yml"


VIM_DIR = TOP_LEVEL / "pack" / "modules" / "start"
VARS_DIR = TOP_LEVEL / ".vars"


INSTALL_SCRIPTS_DIR = CONF_DIR / "scripts"
BIN_DIR = VARS_DIR / "bin"
LIB_DIR = VARS_DIR / "lib"

_MODULES_DIR = VARS_DIR / "modules"
PIP_DIR = _MODULES_DIR / "py_modules"
GEM_DIR = _MODULES_DIR / "rb_modules"
NPM_DIR = _MODULES_DIR
GO_DIR = _MODULES_DIR / "go_modules"


PATH = environ["PATH"] = pathsep.join(
    map(
        normcase,
        chain(
            (
                BIN_DIR,
                PIP_DIR / "bin",
                GEM_DIR / "bin",
                NPM_DIR / "node_modules" / ".bin",
                GO_DIR / "bin",
            ),
            (
                path
                for path in map(PurePath, environ["PATH"].split(pathsep))
                if path != RT_BIN
            ),
        ),
    )
)
environ["PYTHONUSERBASE"] = normcase(PIP_DIR)
GEM_PATH = environ["GEM_PATH"] = pathsep.join(
    map(
        normcase,
        chain(
            (GEM_DIR / "gems",),
            (
                PurePath(path)
                for path in environ.get("GEM_PATH", "").split(pathsep)
                if path
            ),
        ),
    )
)

TMP_DIR = VARS_DIR / "tmp"
LOGS_DIR = VARS_DIR / "logs"
UPDATE_LOG = LOGS_DIR / "last_update.txt"
