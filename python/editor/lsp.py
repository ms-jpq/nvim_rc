from fnmatch import fnmatch
from pathlib import Path
from shutil import which
from typing import Any, Mapping, MutableMapping, Optional

from pynvim import Nvim
from pynvim_pp.api import (
    ask,
    buf_get_lines,
    cur_win,
    get_cwd,
    win_get_buf,
    win_get_cursor,
)
from pynvim_pp.lib import decode, encode
from pynvim_pp.text_object import gen_split
from std2.pickle import new_decoder, new_encoder
from std2.types import never

from ..config.lsp import LspAttrs, RootPattern, RPFallback, lsp_specs
from ..registery import LANG, NAMESPACE, atomic, keymap, rpc
from ..text_objects.word import UNIFIYING_CHARS

_LSP_INIT = (Path(__file__).resolve().parent / "lsp.lua").read_text("UTF-8")

keymap.n("gp") << "<cmd>lua vim.lsp.buf.definition()<cr>"
keymap.n("gP") << "<cmd>lua vim.lsp.buf.references()<cr>"

keymap.n("H") << "<cmd>lua vim.lsp.diagnostic.show_line_diagnostics()<cr>"
keymap.n("K") << "<cmd>lua vim.lsp.buf.hover()<cr>"

keymap.n("gw") << "<cmd>lua vim.lsp.buf.code_action()<cr>"
keymap.v("gw") << "<cmd>lua vim.lsp.buf.range_code_action()<cr>"

keymap.n("<c-p>") << "<cmd>lua vim.lsp.diagnostic.goto_prev()<cr>"
keymap.n("<c-n>") << "<cmd>lua vim.lsp.diagnostic.goto_next()<cr>"


@rpc(blocking=True)
def _rename(nvim: Nvim) -> None:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)
    row, col = win_get_cursor(nvim, win=win)
    line, *_ = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
    b_line = encode(line)
    lhs, rhs = decode(b_line[:col]), decode(b_line[col:])
    split = gen_split(lhs=lhs, rhs=rhs, unifying_chars=UNIFIYING_CHARS)
    word = split.word_lhs + split.word_rhs
    ans = ask(nvim, question=LANG("rename: "), default=word)

    if ans:
        nvim.lua.vim.lsp.buf.rename(ans)


keymap.n("R") << f"<cmd>lua {NAMESPACE}.{_rename.name}()<cr>"


_DECODER = new_decoder[Optional[RootPattern]](Optional[RootPattern])


@rpc(blocking=True)
def _find_root(nvim: Nvim, _pattern: Any, filename: str, bufnr: int) -> Optional[str]:
    pattern: Optional[RootPattern] = _DECODER(_pattern)
    path = Path(filename)

    if not pattern:
        return str(get_cwd(nvim))
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
                return str(get_cwd(nvim))
            elif pattern.fallback is RPFallback.home:
                return str(Path.home())
            elif pattern.fallback is RPFallback.parent:
                return str(path.parent)
            else:
                never(pattern)


@rpc(blocking=True)
def _on_attach(nvim: Nvim, server: str) -> None:
    pass


def _encode_spec(spec: LspAttrs) -> Mapping[str, Any]:
    config: MutableMapping[str, Any] = {}
    if spec.args is not None:
        config["cmd"] = (spec.bin, *spec.args)
    if spec.filetypes:
        config["filetypes"] = tuple(spec.filetypes)
    if spec.init_options:
        config["init_options"] = spec.init_options

    if spec.settings:
        config["settings"] = spec.settings
    return config


_ENCODER = new_encoder[Optional[RootPattern]](Optional[RootPattern])

for spec in lsp_specs:
    if which(spec.bin):
        config = _encode_spec(spec)
        args = (
            NAMESPACE,
            _find_root.name,
            _on_attach.name,
            spec.server,
            config,
            _ENCODER(spec.root),
        )
        atomic.exec_lua(_LSP_INIT, args)

atomic.command("doautoall Filetype")
