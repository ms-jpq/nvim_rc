from pathlib import Path
from shlex import join
from tempfile import NamedTemporaryFile
from typing import Callable, Iterable, MutableMapping, Tuple

from pynvim.api import Buffer, Nvim
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


_jobs: MutableMapping[int, Callable[..., None]]


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

    job = fzf(nvim, args, source)

    def cont() -> None:
        line = Path(tmp.name).read_text()

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
