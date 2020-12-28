from pathlib import Path, PurePath
from urllib.parse import urlparse


from yaml import safe_load

from ..consts import CONF_PACKAGES, VIM_DIR


def _p_name(uri: str) -> Path:
    url = urlparse(uri).path
    return VIM_DIR / PurePath(url).stem

conf = safe_load(CONF_PACKAGES.open())
plugins = tuple(_p_name(c["uri"]) for c in conf)
