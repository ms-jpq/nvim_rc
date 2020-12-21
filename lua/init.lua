local loop = require "loop"
local vim_home = vim.env["XDG_CONFIG_HOME"] .. "/nvim"
local py_main = vim_home .. "/init.py"


loop.spawn(py_main, {vim.v.servername})