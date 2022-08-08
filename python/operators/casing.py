from re import RegexFlag, compile

from pynvim.api.nvim import Nvim
from pynvim_pp.api import buf_get_text, buf_set_text, cur_buf
from pynvim_pp.operators import VisualTypes, operator_marks, writable

from ..registery import NAMESPACE, keymap, rpc


@rpc(blocking=True)
def _snake_case(nvim: Nvim, visual: VisualTypes) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        begin, end = operator_marks(nvim, buf=buf, visual_type=visual)
        if begin < end:
            re = compile(r"(?<!^)(?=[A-Z])", flags=RegexFlag.U)

            lines = buf_get_text(nvim, buf=buf, begin=begin, end=end)
            new_lines = tuple(re.sub("_", line).casefold() for line in lines)
            buf_set_text(nvim, buf=buf, begin=begin, end=end, text=new_lines)


_ = keymap.n("gh") << f"<cmd>set opfunc={_snake_case.name}<cr>g@"
_ = keymap.v("gh") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_snake_case.name}(vim.NIL)<cr>"


@rpc(blocking=True)
def _camel_case(nvim: Nvim, visual: VisualTypes) -> None:
    buf = cur_buf(nvim)
    if not writable(nvim, buf=buf):
        return
    else:
        begin, end = operator_marks(nvim, buf=buf, visual_type=visual)
        if begin < end:
            lines = buf_get_text(nvim, buf=buf, begin=begin, end=end)
            new_lines = tuple(
                "".join(word.title() for word in line.split("_")) for line in lines
            )
            buf_set_text(nvim, buf=buf, begin=begin, end=end, text=new_lines)


_ = keymap.n("gH") << f"<cmd>set opfunc={_camel_case.name}<cr>g@"
_ = keymap.v("gH") << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_camel_case.name}(vim.NIL)<cr>"
