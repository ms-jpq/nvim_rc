from pathlib import PurePath
from typing import Sequence

from pynvim import Nvim
from pynvim_pp.api import cur_buf, buf_name, get_cwd

from ..registery import rpc, settings
from std2.pathlib import longest_common_path


@rpc(blocking=True)
def _statusline(nvim: Nvim, args: Sequence[None]) -> str:
    cwd = PurePath(get_cwd(nvim))
    buf = cur_buf(nvim)
    b_name = buf_name(nvim,buf=buf)

    path = PurePath(b_name)
    ancestor = longest_common_path(cwd, path)
    name = path.relative_to(ancestor) if ancestor else b_name

    return f"{name}"


settings["statusline"] = f"%{{{_statusline.name}()}}"
