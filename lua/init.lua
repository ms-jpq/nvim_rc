local vim_home = vim.env["XDG_CONFIG_HOME"] .. "/nvim"
local py_main = vim_home .. "/init.py"


local on_exit = function (_, code)
  vim.api.nvim_err_writeln("EXITED - " .. code)
end

local on_stderr = function (_, msg)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end


-- vim.g.mapleader = " "
-- vim.g.maplocalleader = " "


local chan = vim.fn.jobstart(
  {py_main},
  { rpc = true, on_exit = on_exit, on_stderr = on_stderr }
)


local notify = function (name, args)
  vim.rpcnotify(chan, name, args)
end
local request = function (name, args)
  return vim.rpcrequest(chan, name, args)
end