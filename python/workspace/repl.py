from itertools import chain
from os import environ
from os.path import normcase
from shutil import which
from typing import Iterator, Mapping, Optional, TypedDict, cast
from uuid import uuid4

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim_pp.api import (
    buf_get_option,
    buf_get_var,
    buf_set_var,
    create_buf,
    cur_win,
    list_bufs,
    win_close,
)
from pynvim_pp.float_win import list_floatwins, open_float_win
from pynvim_pp.lib import write
from pynvim_pp.rpc import RpcCallable


from ..registery import LANG, NAMESPACE, atomic, autocmd, keymap, rpc



