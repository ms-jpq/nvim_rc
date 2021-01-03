from pathlib import Path
from shlex import join
from tempfile import NamedTemporaryFile
from typing import Callable, Iterable, MutableMapping, Sequence, Tuple, cast

from pynvim.api import Buffer, Nvim, Tabpage, Window
from pynvim_pp.float_win import open_float_win
from pynvim_pp.lib import write

from ..registery import keymap, rpc, settings
from .terminal import close_term

# ui for cmd auto complete
settings["wildmenu"] = True
settings["wildmode"] = "list:longest,full"
settings["wildignorecase"] = True
settings["wildoptions"] = "tagfile"


# more history
settings["history"] = 10000


# ignore case
settings["ignorecase"] = True


# use [ ] to navigate various lists, ie quickfix
keymap.n("[b") << "<cmd>bprevious<cr>"
keymap.n("]b") << "<cmd>bnext<cr>"


_jobs: MutableMapping[int, Callable[[], None]] = {}


@rpc(blocking=True)
def _on_exit(nvim: Nvim, args: Tuple[int, int, str]) -> None:
    job_id, code, event_type = args
    post = _jobs.pop(job_id)
    if code in {0, 130}:
        close_term(nvim)
        post()


@rpc(blocking=True)
def fzf(nvim: Nvim, args: Iterable[str], source: Iterable[str]) -> int:
    env = {"FZF_DEFAULT_COMMAND": join(source)}
    opts = {"on_exit": _on_exit.remote_name, "env": env}

    buf: Buffer = nvim.api.create_buf(False, True)
    nvim.api.buf_set_option(buf, "bufhidden", "wipe")
    open_float_win(nvim, margin=0, relsize=0.95, buf=buf)

    job: int = nvim.funcs.termopen(tuple(("fzf", *args)), opts)
    nvim.command("startinsert")
    return job


def _switch_to_path(nvim: Nvim, path: str) -> None:
    wins: Sequence[Window] = nvim.api.list_wins()
    for win in wins:
        buf: Buffer = nvim.api.win_get_buf(win)
        filename: str = nvim.api.buf_get_name(buf)
        if filename == path:
            nvim.api.set_current_win(win)
            break
    else:
        tab: Tabpage = nvim.api.get_current_tabpage()
        win = nvim.api.get_current_win()
        wins = nvim.api.tabpage_list_wins(tab)
        for win in (win, *wins):
            buf = nvim.api.win_get_buf(win)
            filename: str = nvim.api.buf_get_name(buf)
            if Path(filename).exists():
                nvim.api.win_set_buf(win, buf)
                nvim.api.set_current_win(win)
                break
            else:
                nvim.command("vnew")
                win = nvim.api.get_current_win()
                nvim.api.win_set_buf(win, buf)


@rpc(blocking=True)
def fzf_files(nvim: Nvim) -> None:
    with NamedTemporaryFile() as tmp:
        exc = f"abort+execute:mv {{f}} {tmp.name}"

    args = (
        # "--read0",
        "--print0",
        "--preview",
        "preview {}",
        "--bind",
        f"enter:{exc}",
        "--bind",
        f"double-click:{exc}",
    )
    source = (
        "fd",
        # "--print0",
        "--hidden",
        "--follow",
        "--type",
        "file",
        "--type",
        "symlink",
    )

    job = cast(int, fzf(nvim, args, source))

    def cont() -> None:
        path = Path(tmp.name)
        if path.exists():
            line = path.read_text()
            _switch_to_path(nvim, path=line)

    _jobs[job] = cont


keymap.n("<leader>p") << f"<cmd>lua {fzf_files.remote_name}()<cr>"


#   keys:
#     - modes: n
#       maps:
#         "<c-p>": "<cmd>Commands<cr>"
#         "<c-n>": "<cmd>History:<cr>"
#         "<leader>p": "<cmd>Files<cr>"
#         "<leader>P": "<cmd>History<cr>"
#         "<leader>o": "<cmd>BLines<cr>"
#         "<leader>I": "<cmd>Buffers<cr>"
#     - modes: n
#       opts:
#         silent: False
#       maps:
#         "<leader>O": ":Rg "
#   lua: |-
#     vim.env["FZF_DEFAULT_OPTS"] = vim.env["FZF_DEFAULT_OPTS"] .. " --no-border"
