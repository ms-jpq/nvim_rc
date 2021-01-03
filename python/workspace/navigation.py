from typing import Tuple

from pynvim.api.nvim import Nvim
from pynvim_pp.lib import write

from ..registery import keymap, rpc, settings
from .terminal import close_term, open_term

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


@rpc(blocking=True)
def _on_exit(nvim: Nvim, args: Tuple[int, int, str]) -> None:
    job_id, code, event_type = args
    if code in {0, 130}:
        close_term(nvim)


@rpc(blocking=True)
def fzf(nvim: Nvim, *args: str) -> None:
    open_term(nvim, "fzf", *args, on_exit=_on_exit)


@rpc(blocking=True)
def fzf_files(nvim: Nvim) -> None:
    fzf(nvim, "--preview", "preview {}")


keymap.n("<leader>p") << f"<cmd>lua {fzf_files.remote_name}()<cr>"

# - uri: https://github.com/junegunn/fzf

# - uri: https://github.com/junegunn/fzf.vim
#   vals:
#     fzf_buffers_jump: True
#     fzf_preview_window: right:wrap
#     fzf_layout:
#       window:
#         width: 0.9
#         height: 0.9
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
