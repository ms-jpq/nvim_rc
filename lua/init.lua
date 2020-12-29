local nvim_home = vim.api.nvim_list_runtime_paths()[1]
local py_main = nvim_home .. "/init.py"


local _env = function ()
  local pip_home = nvim_home .. "/vars/requirements"
  if vim.env["PYTHONPATH"] then
    return { PYTHONPATH = pip_home .. ":" .. vim.env["PYTHONPATH"] }
  else
    return { PYTHONPATH = pip_home }
  end
end


local on_exit = function (_, code)
  vim.api.nvim_err_writeln("EXITED - " .. code)
end


local on_stderr = function (_, msg)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end


local chan = vim.fn.jobstart(
  {py_main},
  { rpc = true,
    env = _env(),
    on_exit = on_exit,
    on_stderr = on_stderr })


local request = function (name, args)
  return vim.rpcrequest(chan, name, args)
end