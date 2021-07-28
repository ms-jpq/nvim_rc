from itertools import chain
from re import escape

from pynvim.api import Buffer
from pynvim.api.nvim import Nvim
from pynvim_pp.api import buf_get_lines, buf_linefeed, cur_buf
from pynvim_pp.lib import async_call, go
from pynvim_pp.operators import VisualTypes, operator_marks
from std2.lex import escape as lex_esc

from ..registery import keymap, rpc


# search and highlight
def _magic_escape(text: str) -> str:
    rules = {
        "\\": "\\",
        "/": "\\",
        "\n": "\\",
        "\r": "\\",
        "\t": "\\",
    }
    return "".join(lex_esc(text, replace=False, escape=rules))


def _hl_text(nvim: Nvim, text: str) -> None:
    nvim.funcs.setreg("/", _magic_escape(text))

    def cont() -> None:
        nvim.options["hlsearch"] = True

    go(nvim, aw=async_call(nvim, cont))


def _get_selected(nvim: Nvim, buf: Buffer, visual_type: VisualTypes) -> str:
    (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=visual_type)
    linefeed = buf_linefeed(nvim, buf=buf)
    lines = buf_get_lines(nvim, buf=buf, lo=row1, hi=row2 + 1)

    if len(lines) == 1:
        return lines[0].encode()[col1 : col2 + 1].decode()
    else:
        head = lines[0].encode()[col1:].decode()
        body = lines[1:-1]
        tail = lines[-1].encode()[: col2 + 1].decode()
        return linefeed.join(chain((head,), body, (tail,)))


def _hl_selected(nvim: Nvim, visual: VisualTypes) -> str:
    buf = cur_buf(nvim)
    selected = _get_selected(nvim, buf=buf, visual_type=visual)
    _hl_text(nvim, text=selected)
    return selected


@rpc(blocking=True)
def _op_search(nvim: Nvim, visual: VisualTypes = None) -> None:
    _hl_selected(nvim, visual=visual)


@rpc(blocking=True)
def _op_fzf(nvim: Nvim, visual: VisualTypes = None) -> None:
    text = _hl_selected(nvim, visual=visual)
    cont = lambda: nvim.command(f"BLines {text}")
    go(nvim, aw=async_call(nvim, cont))


@rpc(blocking=True)
def _op_rg(nvim: Nvim, visual: VisualTypes = None) -> None:
    text = _hl_selected(nvim, visual=visual)
    escaped = escape(text).replace(r"\ ", " ")
    cont = lambda: nvim.command(f"Rg {escaped}")
    go(nvim, aw=async_call(nvim, cont))


keymap.n("gs") << f"<cmd>set opfunc={_op_search.name}<cr>g@"
keymap.v("gs") << f"<esc><cmd>lua {_op_search.name}()<cr>"

keymap.n("gf") << f"<cmd>set opfunc={_op_fzf.name}<cr>g@"
keymap.v("gf") << f"<esc><cmd>lua {_op_fzf.name}()<cr>"

keymap.n("gF") << f"<cmd>set opfunc={_op_rg.name}<cr>g@"
keymap.v("gF") << f"<esc><cmd>lua {_op_rg.name}()<cr>"


# replace selection
# no magic
@rpc(blocking=True)
def _op_sd(nvim: Nvim, visual: VisualTypes = None) -> None:
    buf = cur_buf(nvim)
    selected = _get_selected(nvim, buf=buf, visual_type=visual)
    escaped = _magic_escape(selected)
    instruction = f":%s/{escaped}//g<left><left>"
    nvim.api.input(instruction)


keymap.n("gt") << f"<cmd>set opfunc={_op_sd.name}<cr>g@"
keymap.v("gt") << f"<esc><cmd>lua {_op_sd.name}()<cr>"

# very magic
keymap.n("gT", silent=False) << ":%s/\\v//g<left><left><left>"
