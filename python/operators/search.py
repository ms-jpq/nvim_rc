from pynvim.api.buffer import Buffer
from pynvim.api.nvim import Nvim
from pynvim_pp.operators import VisualTypes, escape, get_selected

from ..registery import keymap, rpc


# search and highlight
def _magic_escape(text: str) -> str:
    rules = {"\\": "\\\\", "/": "\\/", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    return "".join(escape(text, escape=rules))


def _hl_text(nvim: Nvim, text: str) -> None:
    nvim.funcs.setreg("/", _magic_escape(text))
    nvim.command("set hlsearch")


def _hl_selected(nvim: Nvim, visual: VisualTypes) -> str:
    buf: Buffer = nvim.api.get_current_buf()
    selected = get_selected(nvim, buf=buf, visual_type=visual)
    _hl_text(nvim, text=selected)
    return selected


@rpc(blocking=True)
def _op_search(nvim: Nvim, visual: VisualTypes = None) -> None:
    _hl_selected(nvim, visual=visual)


@rpc(blocking=True)
def _op_fzf(nvim: Nvim, visual: VisualTypes = None) -> None:
    text = _hl_selected(nvim, visual=visual)
    nvim.command(f"BLines {text}")


@rpc(blocking=True)
def _op_rg(nvim: Nvim, visual: VisualTypes = None) -> None:
    text = _hl_selected(nvim, visual=visual)
    nvim.command(f"Rg {text}")


keymap.n("gs") << f"<cmd>set opfunc={_op_search.remote_name}<cr>g@"
keymap.v("gs") << f"<esc><cmd>lua {_op_search.remote_name}()<cr>"

keymap.n("gf") << f"<cmd>set opfunc={_op_fzf.remote_name}<cr>g@"
keymap.v("gf") << f"<esc><cmd>lua {_op_fzf.remote_name}()<cr>"

keymap.n("gF") << f"<cmd>set opfunc={_op_rg.remote_name}<cr>g@"
keymap.v("gF") << f"<esc><cmd>lua {_op_rg.remote_name}()<cr>"


# replace selection
# no magic
@rpc(blocking=True)
def _op_sd(nvim: Nvim, visual: VisualTypes = None) -> None:
    buf: Buffer = nvim.api.get_current_buf()
    selected = get_selected(nvim, buf=buf, visual_type=visual)
    escaped = _magic_escape(selected)
    instruction = f":%s/{escaped}//g<left><left>"
    nvim.api.input(instruction)


keymap.n("gt") << f"<cmd>set opfunc={_op_sd.remote_name}<cr>g@"
keymap.v("gt") << f"<esc><cmd>lua {_op_sd.remote_name}()<cr>"

# very magic
keymap.n("gT", silent=False) << ":%s/\\v//g<left><left><left>"
