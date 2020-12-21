from functools import partial
from os import environ, listdir
from os.path import abspath, dirname, expanduser, join

TOP_LEVEL = dirname(dirname(dirname(dirname(abspath(__file__)))))
_SUB_MODULES = join(TOP_LEVEL, "submodules")
SUB_MODULES = tuple(map(partial(join, _SUB_MODULES), listdir(_SUB_MODULES)))


XDG_DATA_HOME = environ.get("XDG_DATA_HOME", join(expanduser("~"), ".local", "share"))
