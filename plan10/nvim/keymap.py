from pynvim import Nvim

from typing import Mapping, Any


class KM:
    pass


class KeyMap:
    _conf: Mapping[str, str] = {}

    def __getattr__(self, key: str) -> KM:
        if key not in {"n", "o", "v", "t"}:
          raise AttributeError()
        else:
          return KM()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return super().__call__(*args, **kwds)


keymap = KeyMap()


async def finalize(nvim: Nvim) -> None:
    pass