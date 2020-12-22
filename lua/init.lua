local vim_home = vim.env["XDG_CONFIG_HOME"] .. "/nvim"
local py_main = vim_home .. "/init.py"


local on_exit = function (_, code)
  vim.api.nvim_err_writeln("EXITED - " .. code)
end

local on_stderr = function (_, msg)
  vim.api.nvim_err_writeln(table.concat(msg, "\n"))
end

local chan = vim.fn.jobstart(
  {py_main},
  { rpc = true, on_exit = on_exit, on_stderr = on_stderr }
)


lv = {}
lv.notify = function (event, args)
  vim.rpcnotify(chan, event, args)
end
lv.request = function (event, args)
  return vim.rpcrequest(chan, evnt, args)
end


lv.notify("EVENT", {"ARG1", "ARG2", "ARG3"})
