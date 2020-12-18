from os.path import dirname, abspath, expanduser, join
from os import environ

TOP_LEVEL = dirname(dirname(dirname(dirname(abspath(__file__)))))

XDG_DATA_HOME = environ.get("XDG_DATA_HOME", join(expanduser("~"), ".local", "share"))