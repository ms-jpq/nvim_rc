from itertools import chain
from os import environ, name, pathsep
from os.path import normcase
from pathlib import Path, PurePath
from sys import executable

IS_WIN = name == "nt"

DATE_FMT = "%Y-%m-%d %X"

TOP_LEVEL = Path(__file__).resolve(strict=True).parent.parent

VIM_DIR = TOP_LEVEL / "pack" / "modules" / "start"
VARS_DIR = TOP_LEVEL / "var"

RT_DIR = VARS_DIR / "runtime"
RT_SCRIPTS = (
    "Scripts"
    if IS_WIN and not ({"msys64", "bin"} <= {Path(executable).resolve().parts})
    else "bin"
)
_RT_BIN = RT_DIR / RT_SCRIPTS
RT_PY = _RT_BIN / PurePath(executable).name

DEADLINE = 3600

REQUIREMENTS = TOP_LEVEL / "requirements.txt"
INSTALL_SCRIPT = TOP_LEVEL / "install.sh"

LANG_ROOT = TOP_LEVEL / "locale"
DEFAULT_LANG = "c"


CONF_DIR = TOP_LEVEL / "config"
CONF_PKGS = CONF_DIR / "packages.yml"
CONF_LSP = CONF_DIR / "lsp.yml"
CONF_LINT = CONF_DIR / "lint.yml"
CONF_FMT = CONF_DIR / "fmt.yml"
CONF_TOOL = CONF_DIR / "tools.yml"


LIBEXEC = TOP_LEVEL / "libexec"
DLEXEC = CONF_DIR / "dl"
BIN_DIR = VARS_DIR / "bin"
LIB_DIR = VARS_DIR / "lib"

_MODULES_DIR = VARS_DIR / "modules"

PIP_DIR = _MODULES_DIR / "py_modules"
GEM_DIR = _MODULES_DIR / "rb_modules"
NPM_DIR = _MODULES_DIR

_PIP_BIN = PIP_DIR / RT_SCRIPTS

PATH = environ["PATH"] = pathsep.join(
    map(
        normcase,
        chain(
            (
                BIN_DIR,
                GEM_DIR / "bin",
                NPM_DIR / "node_modules" / ".bin",
            ),
            (
                path
                for path in map(PurePath, environ["PATH"].split(pathsep))
                if path != _RT_BIN
            ),
            (_PIP_BIN,),
        ),
    )
)

TMP_DIR = VARS_DIR / "tmp"
UPDATE_LOG = TMP_DIR / "last_update.txt"
