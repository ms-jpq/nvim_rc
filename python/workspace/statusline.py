from pathlib import Path

from ..registery import atomic

_status = Path(__file__).with_suffix(".lua").read_text()

_preview = "%w"
_ql = "%q"
_name = "%F"
_modified = "%m"

_lsp = "%{v:lua.LSP_status_line()}"
_tabs = "%{&expandtab ? &tabstop .. 'S' : 'T'}"
_ft = "%Y"
_scroll = "%3p%%"
_pos = "%4l:%-4c"

_lhs = f"{_preview}{_ql}{_name}{_modified}"
_rhs = f"{_lsp} | {_tabs} | {_ft} | {_scroll} | {_pos}"
_line = f"{_lhs} %= {_rhs}"

atomic.exec_lua(_status, ())
atomic.set_option("statusline", _line)
