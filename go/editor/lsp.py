from fnmatch import fnmatch
from os.path import normcase
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Optional

from pynvim_pp.handler import GLOBAL_NS
from pynvim_pp.lib import decode, encode
from pynvim_pp.nvim import Nvim
from pynvim_pp.text_object import gen_split
from pynvim_pp.types import NoneType
from pynvim_pp.window import Window
from std2.pickle.decoder import new_decoder
from std2.pickle.encoder import new_encoder
from std2.types import never

from ..config.install import which
from ..config.lsp import LspAttrs, RootPattern, RPFallback, lsp_specs
from ..registry import LANG, NAMESPACE, atomic, autocmd, keymap, rpc, settings
from ..text_objects.word import UNIFIYING_CHARS

_LSP_INIT = Path(__file__).resolve(strict=True).with_name("lsp.lua").read_text("UTF-8")

settings["tagfunc"] = "v:lua.vim.lsp.tagfunc"
settings["formatexpr"] = "v:lua.vim.lsp.formatexpr()"

_ = keymap.n("gp") << "<cmd>lua vim.lsp.buf.definition()<cr>"
_ = keymap.n("gP") << "<cmd>lua vim.lsp.buf.references()<cr>"

_ = keymap.n("H") << "<cmd>lua vim.diagnostic.open_float()<cr>"

_ = keymap.n("gm") << "<cmd>lua vim.lsp.buf.document_symbol()<cr>"
_ = keymap.n("gM") << "<cmd>lua vim.lsp.buf.workspace_symbol()<cr>"

_ = keymap.n("<leader>j") << "<cmd>lua vim.diagnostic.setloclist()<cr>"
_ = keymap.n("<leader>J") << "<cmd>lua vim.diagnostic.setqflist()<cr>"

_ = (
    keymap.n("<c-p>")
    << "<cmd>lua vim.diagnostic.goto_prev { severity = vim.diagnostic.severity.ERROR }<cr>"
)
_ = (
    keymap.n("<c-n>")
    << "<cmd>lua vim.diagnostic.goto_next { severity = vim.diagnostic.severity.ERROR }<cr>"
)


# _ = keymap.n("<leader>z") << "<cmd>LspRestart<cr>"

_ = (
    autocmd("BufEnter", "CursorHold", "InsertLeave", modifiers=("<buffer>"))
    << "silent! lua vim.lsp.codelens.refresh()"
)
_ = (
    autocmd("CursorHold", "CursorHoldI", modifiers=("<buffer>"))
    << "silent! lua vim.lsp.buf.document_highlight()"
)
_ = (
    autocmd("CursorMoved", modifiers=("<buffer>"))
    << "silent! lua vim.lsp.buf.clear_references()"
)


@rpc()
async def _rename() -> None:
    win = await Window.get_current()
    buf = await win.get_buf()
    row, col = await win.get_cursor()
    line, *_ = await buf.get_lines(lo=row, hi=row + 1)

    b_line = encode(line)
    lhs, rhs = decode(b_line[:col]), decode(b_line[col:])
    split = gen_split(lhs=lhs, rhs=rhs, unifying_chars=UNIFIYING_CHARS)
    word = split.word_lhs + split.word_rhs
    if ans := await Nvim.input(question=LANG("rename: "), default=word):
        await Nvim.lua.vim.lsp.buf.rename(NoneType, ans)


_ = keymap.n("R") << f"<cmd>lua {NAMESPACE}.{_rename.method}()<cr>"


_DECODER = new_decoder[Optional[RootPattern]](Optional[RootPattern])


@rpc()
async def _find_root(r_pattern: Any, filename: str, bufnr: int) -> Optional[str]:
    pattern: Optional[RootPattern] = _DECODER(r_pattern)
    path = Path(filename)

    if not pattern:
        return str(await Nvim.getcwd())
    else:
        for parent in path.parents:
            for member in parent.iterdir():
                name = member.name
                if name in pattern.exact:
                    return str(parent)
                else:
                    for glob in pattern.glob:
                        if fnmatch(name, glob):
                            return str(parent)
        else:
            if pattern.fallback is RPFallback.none:
                return None
            elif pattern.fallback is RPFallback.cwd:
                return str(await Nvim.getcwd())
            elif pattern.fallback is RPFallback.home:
                return str(Path.home())
            elif pattern.fallback is RPFallback.parent:
                return str(path.parent)
            else:
                never(pattern.fallback)


@rpc()
async def _on_attach(_: str) -> None:
    pass


def _encode_spec(spec: LspAttrs) -> Mapping[str, Any]:
    config: MutableMapping[str, Any] = {}
    if spec.args is not None:
        config["cmd"] = (normcase(spec.bin), *spec.args)
    if spec.filetypes:
        config["filetypes"] = tuple(spec.filetypes)
    if spec.init_options:
        config["init_options"] = spec.init_options

    if spec.settings:
        config["settings"] = spec.settings
    return config


_ENCODER = new_encoder[Optional[RootPattern]](Optional[RootPattern])

for server, spec in lsp_specs().items():
    if spec and which(spec.bin):
        config = _encode_spec(spec)
        args = (
            GLOBAL_NS,
            str(_find_root.uuid),
            str(_on_attach.uuid),
            normcase(server),
            config,
            _ENCODER(spec.root),
        )
        atomic.exec_lua(_LSP_INIT, args)


atomic.command("silent! doautoall Filetype")
