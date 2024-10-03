from importlib.resources import files
from pathlib import Path

from ..registry import atomic

_status = files(__package__).joinpath("statusline.lua").read_text("UTF-8")

_preview = "%w"
_ql = "%q"
_name = "%f"
_modified = "%m"

_lsp = "%{v:lua.Go.LSP_status_line()}"
_ft = "%y"
_tabs = "%{&tabstop .. (&expandtab ? 'S' : 'T')}"
_linefeed = "%{&fileformat}"
_pos = "%5l:%-3c"
_scroll = "%3p%%"

_lhs = f"{_preview}{_ql}{_name}{_modified}"
_rhs = f"{_lsp} | {_ft} {_tabs} {_linefeed} @{_pos}≡ {_scroll}"
_line = f"{_lhs} %= {_rhs}"

atomic.exec_lua(_status, ())
atomic.set_option("statusline", _line)
