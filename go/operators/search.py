from re import escape
from types import NoneType

from pynvim_pp.buffer import Buffer
from pynvim_pp.nvim import Nvim
from pynvim_pp.operators import VisualTypes, operator_marks

from ..registery import NAMESPACE, keymap, rpc


# search and highlight
def _magic_escape(text: str) -> str:
    rules = {
        "\\": r"\\",
        "/": r"\/",
        "\n": r"\n",
        "\r": r"\r",
        "\t": r"\t",
    }
    print(rules)
    return text.translate(str.maketrans(rules))


async def _hl_text(text: str) -> None:
    await Nvim.fn.setreg(NoneType, "/", _magic_escape(text))
    await Nvim.opts.set("hlsearch", val=True)


async def _get_selected(buf: Buffer, visual_type: VisualTypes) -> str:
    begin, end = await operator_marks(buf, visual_type=visual_type)
    linesep = await buf.linefeed()
    lines = await buf.get_text(begin=begin, end=end)
    return linesep.join(lines)


async def _hl_selected(visual: VisualTypes) -> str:
    buf = await Buffer.get_current()
    selected = await _get_selected(buf=buf, visual_type=visual)
    await _hl_text(selected)
    return selected


@rpc(schedule=True)
async def _op_search(visual: VisualTypes) -> None:
    await _hl_selected(visual)


@rpc(schedule=True)
async def _op_fzf(visual: VisualTypes) -> None:
    text = await _hl_selected(visual)
    await Nvim.exec(f"BLines {text}")


@rpc(schedule=True)
async def _op_rg(visual: VisualTypes) -> None:
    text = await _hl_selected(visual)
    escaped = escape(text).replace(r"\ ", " ")
    await Nvim.exec(f"Rg {escaped}")


_ = keymap.n("gs") << f"<cmd>set opfunc={_op_search.method}<cr>g@"
_ = (
    keymap.v("gs")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_op_search.method}(vim.NIL)<cr>"
)

_ = keymap.n("gf") << f"<cmd>set opfunc={_op_fzf.method}<cr>g@"
_ = keymap.v("gf") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_op_fzf.method}(vim.NIL)<cr>"

_ = keymap.n("gF") << f"<cmd>set opfunc={_op_rg.method}<cr>g@"
_ = keymap.v("gF") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_op_rg.method}(vim.NIL)<cr>"


# replace selection
# no magic
@rpc()
async def _op_sd(visual: VisualTypes) -> None:
    buf = await Buffer.get_current()
    selected = await _get_selected(buf, visual_type=visual)
    escaped = _magic_escape(selected)
    instruction = rf":%s/\V{escaped}//g<left><left>"
    await Nvim.api.input(NoneType, instruction)


_ = keymap.n("gt") << f"<cmd>set opfunc={_op_sd.method}<cr>g@"
_ = keymap.v("gt") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_op_sd.method}(vim.NIL)<cr>"

# very magic
_ = keymap.n("gT", silent=False) << r":%s/\v//g<left><left><left>"
