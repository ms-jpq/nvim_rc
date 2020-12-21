local loop = require "loop"
local vim_home = vim.env["XDG_CONFIG_HOME"] .. "/nvim"
local py_main = vim_home .. "/init.py"


local chan = vim.fn.jobstart({py_main}, { rpc = true })
vim.rpcnotify(chan, "EVENT", {"ARG1", "ARG2", "ARG3"})