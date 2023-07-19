from io import StringIO
from locale import getlocale
from string import Template
from typing import Mapping, MutableMapping, Optional, Union

from pynvim_pp.lib import decode
from std2.pickle.decoder import new_decoder
from yaml import safe_load

from ..consts import DEFAULT_LANG, LANG_ROOT


def _get_lang(code: Optional[str], fallback: str) -> str:
    if code:
        return code.casefold()
    else:
        tag, _ = getlocale()
        tag = (tag or fallback).casefold()
        primary, _, _ = tag.partition("-")
        lang, _, _ = primary.partition("_")
        return lang


class Lang:
    def __init__(self, specs: Mapping[str, str]) -> None:
        self._specs: MutableMapping[str, str] = {}
        self._specs.update(specs)

    def __call__(self, key: str, **kwds: Union[str, int, float]) -> str:
        spec = self._specs[key]
        return Template(spec).substitute(kwds)


def load(code: Optional[str]) -> Lang:
    lang = _get_lang(code, fallback=DEFAULT_LANG)
    coder = new_decoder[Mapping[str, str]](Mapping[str, str])

    lang_path = (LANG_ROOT / lang).with_suffix(".yml")
    yml_path = (
        lang_path
        if lang_path.exists()
        else (LANG_ROOT / DEFAULT_LANG).with_suffix(".yml")
    )

    yml = decode(yml_path.read_bytes())
    with StringIO() as io:
        io.write(yml)
        io.seek(0)
        specs = coder(safe_load(io))
    return Lang(specs=specs)
