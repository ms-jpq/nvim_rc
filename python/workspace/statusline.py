from pathlib import Path

from ..registery import atomic

_status = Path(__file__).with_suffix(".lua").read_text()

_preview = "%w"
_ql = "%q"
_name = "%F"
_modified = "%m"

_lsp = "%{v:lua.LSP_status_line()}"
_ft = "%y"
_tabs = "%{&expandtab ? &tabstop .. 'S' : 'T'}"
_pos = "%5l:%-3c"
_scroll = "%3p%%"

_lhs = f"{_preview}{_ql}{_name}{_modified}"
_rhs = f"{_lsp} | {_ft} {_tabs}{_pos}{_scroll}"
_line = f"{_lhs} %= {_rhs}"

atomic.exec_lua(_status, ())
atomic.set_option("statusline", _line)
