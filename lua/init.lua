local nvim_home = vim.api.nvim_list_runtime_paths()[1]
local py_main = nvim_home .. "/init.py"


local on_exit = function (_, code)
  vim.api.nvim_err_writeln("EXITED - " .. code)
end


local on_stderr = function (_, msg)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end


local chan = vim.fn.jobstart(
  {py_main},
  { rpc = true,
    on_exit = on_exit,
    on_stderr = on_stderr })

-- vim.rpcrequest(chan, name, args)