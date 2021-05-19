from pathlib import PurePath
from typing import Any, MutableMapping, Sequence, Tuple

from pynvim import Nvim
from pynvim.api import Buffer, Window
from pynvim_pp.api import (
    buf_filetype,
    buf_get_lines,
    buf_get_option,
    buf_line_count,
    buf_name,
    cur_buf,
    cur_win,
    get_cwd,
    win_get_buf,
    win_get_cursor,
)
from std2.pathlib import longest_common_path

from ..registery import rpc, settings

# lv.light_line_errors = function ()
# local count = buf_diagnostics_count("Error")
# return count > 0 and "⛔️ [" .. count .. "]" or ""
# end
# lv.light_line_warnings = function ()
# local count = buf_diagnostics_count("Warning")
# return count > 0 and "⚠️  [" .. count .. "]" or ""
# end


def _scroll_pos(nvim: Nvim, win: Window, buf: Buffer) -> Tuple[str, str]:
    row, col = win_get_cursor(nvim, win=win)
    line, *_ = buf_get_lines(nvim, buf=buf, lo=row, hi=row + 1)
    rows = buf_line_count(nvim, buf=buf)

    r, c = row + 1, len(line.encode()[:col].decode()) + 1
    scroll = format(r / rows, "4.0%")
    pos = f"{r}:{c}".center(8)

    return scroll, pos


def _indent(nvim: Nvim, buf: Buffer) -> str:
    expand_tab: bool = buf_get_option(nvim, buf=buf, key="expandtab")
    tabstop: int = buf_get_option(nvim, buf=buf, key="tabstop")
    indent = ("spaces" if expand_tab else "tabs") + f" {tabstop}"
    return indent


_LSP_CLIENTS = """
return (function ()
  local clients = vim.lsp.buf_get_clients(0)
  local acc = {}
  for _, client in ipairs(clients) do
    local warnings = vim.lsp.diagnostic.get_count(0, "Warning", client.id)
    local errors = vim.lsp.diagnostic.get_count(0, "Error", client.id)
    table.insert(acc, {name=client.name, warnings=warnings, errors=errors})
  end
  return acc
end)()
"""


def _lsp(nvim: Nvim) -> str:
    clients = nvim.api.exec_lua(_LSP_CLIENTS, ())
    lsp_stats: MutableMapping[str, Tuple[int, int]] = {}
    for client in clients:
        name = client["name"]
        warnings, errors = lsp_stats.setdefault(name, (0, 0))
        warnings += client["warnings"]
        errors += client["errors"]
        lsp_stats[name] = warnings, errors

    lsp = f"[{' '.join(lsp_stats.keys())}]"
    return lsp


@rpc(blocking=True)
def _lhs(nvim: Nvim, _: Sequence[None]) -> str:
    cwd = PurePath(get_cwd(nvim))
    buf = cur_buf(nvim)
    b_name = buf_name(nvim, buf=buf)

    path = PurePath(b_name)
    ancestor = longest_common_path(cwd, path)
    name = path.relative_to(ancestor) if ancestor else b_name

    return f"{name}"


@rpc(blocking=True)
def _rhs(nvim: Nvim, _: Any) -> str:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)

    scroll, pos = _scroll_pos(nvim, win=win, buf=buf)
    ft = buf_filetype(nvim, buf=buf)
    indent = _indent(nvim, buf=buf)
    lsp = _lsp(nvim)

    return f"{lsp} | {indent} | {ft} | {scroll} | {pos}"


settings["statusline"] = f"%{{{_lhs.name}()}}%=%{{{_rhs.name}()}}"
