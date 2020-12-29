local nvim_home = vim.api.nvim_list_runtime_paths()[1]
local py_main = nvim_home .. "/init.py"
local pip_home = nvim_home .. "vars/pip_modules"


if vim.env["PYTHONPATH"] then
  vim.env["PYTHONPATH"] =  pip_home .. ":" .. vim.env["PYTHONPATH"]
else
  vim.env["PYTHONPATH"] = pip_home
end


local on_exit = function (_, code)
  vim.api.nvim_err_writeln("EXITED - " .. code)
end


local on_stderr = function (_, msg)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end


local chan = vim.fn.jobstart(
  {py_main},
  { rpc = true, on_exit = on_exit, on_stderr = on_stderr }
)


local request = function (name, args)
  return vim.rpcrequest(chan, name, args)
end