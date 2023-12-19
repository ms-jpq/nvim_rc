from textwrap import dedent

from pynvim_pp.buffer import Buffer
from pynvim_pp.lib import encode
from pynvim_pp.nvim import Nvim
from pynvim_pp.operators import VisualTypes, operator_marks
from pynvim_pp.window import Window

from ..registry import NAMESPACE, keymap, rpc


@rpc()
async def _go_replace(visual: VisualTypes) -> None:
    buf = await Buffer.get_current()
    if not await buf.modifiable():
        return
    else:
        linefeed = await buf.linefeed()
        (r1, c1), (r2, c2) = await operator_marks(buf, visual_type=visual)
        lines = await buf.get_lines(lo=r1, hi=r2 + 1)

        if len(lines) > 1:
            h, *_, t = lines
        else:
            h, *_ = t, *_ = lines

        begin = (r1, min(c1, max(0, len(encode(h)) - 1)))
        end = (r2, min(len(encode(t)), c2))

        text = await Nvim.fn.getreg(str)
        if new_lines := text.split(linefeed):
            if n := new_lines.pop():
                new_lines.append(n)

        undolevels = await Nvim.opts.get(int, "undolevels")
        await Nvim.opts.set("undolevels", undolevels)
        await buf.set_text(begin=begin, end=end, text=new_lines)


_ = keymap.n("gr") << f"<cmd>set opfunc={_go_replace.method}<cr>g@"
_ = (
    keymap.v("gr")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_go_replace.method}(vim.NIL)<cr>"
)


@rpc()
async def _go_replace_line() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    if not await buf.modifiable():
        return
    else:
        linefeed = await buf.linefeed()
        row, _ = await win.get_cursor()
        body = await Nvim.fn.getreg(str)
        dedented = dedent(body)

        if new_lines := dedented.split(linefeed):
            if n := new_lines.pop():
                new_lines.append(n)

        await buf.set_lines(lo=row, hi=row + 1, lines=new_lines)


_ = keymap.n("grr") << f"<cmd>lua {NAMESPACE}.{_go_replace_line.method}()<cr>"
