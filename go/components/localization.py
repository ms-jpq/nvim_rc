from locale import getdefaultlocale
from string import Template
from typing import Mapping, MutableMapping, Optional, Union

from std2.pickle.decoder import new_decoder
from yaml import safe_load

from ..consts import DEFAULT_LANG, LANG_ROOT


def _get_lang(code: Optional[str], fallback: str) -> str:
    if code:
        return code.casefold()
    else:
        tag, _ = getdefaultlocale()
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
    lang_path = (LANG_ROOT / lang).with_suffix(".yml")
    yml_path = (
        lang_path
        if lang_path.exists()
        else (LANG_ROOT / DEFAULT_LANG).with_suffix(".yml")
    )

    specs = new_decoder[Mapping[str, str]](Mapping[str, str])(
        safe_load(yml_path.open())
    )
    return Lang(specs=specs)
