from re import RegexFlag, compile

from pynvim_pp.buffer import Buffer
from pynvim_pp.operators import VisualTypes, operator_marks

from ..registry import NAMESPACE, keymap, rpc


@rpc()
async def _snake_case(visual: VisualTypes) -> None:
    buf = await Buffer.get_current()
    if not await buf.modifiable():
        return
    else:
        begin, end = await operator_marks(buf, visual_type=visual)
        if begin < end:
            re = compile(r"(?<!^)(?=[A-Z])", flags=RegexFlag.U)

            lines = await buf.get_text(begin=begin, end=end)
            new_lines = tuple(re.sub("_", line).casefold() for line in lines)
            await buf.set_text(begin=begin, end=end, text=new_lines)


_ = keymap.n("gh") << f"<cmd>set opfunc={_snake_case.method}<cr>g@"
_ = (
    keymap.v("gh")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_snake_case.method}(vim.NIL)<cr>"
)


@rpc()
async def _camel_case(visual: VisualTypes) -> None:
    buf = await Buffer.get_current()
    if not await buf.modifiable():
        return
    else:
        begin, end = await operator_marks(buf, visual_type=visual)
        if begin < end:
            lines = await buf.get_text(begin=begin, end=end)
            new_lines = tuple(
                "".join(word.title() for word in line.split("_")) for line in lines
            )
            await buf.set_text(begin=begin, end=end, text=new_lines)


_ = keymap.n("gH") << f"<cmd>set opfunc={_camel_case.method}<cr>g@"
_ = (
    keymap.v("gH")
    << rf"<c-\><c-n><cmd>lua {NAMESPACE}.{_camel_case.method}(vim.NIL)<cr>"
)
