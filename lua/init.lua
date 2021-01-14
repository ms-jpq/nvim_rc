local nvim_home = vim.api.nvim_list_runtime_paths()[1]
local py_main = "python"

local on_exit = function(_, code)
  vim.api.nvim_err_writeln("EXITED - " .. code)
end

local on_stdout = function(_, msg)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end

local on_stderr = function(_, msg)
  vim.api.nvim_err_write(table.concat(msg, "\n"))
end

local args = {"python3", "-m", py_main, "--socket", vim.v.servername}
local params = {
  cwd = nvim_home,
  on_exit = on_exit,
  on_stdout = on_stdout,
  on_stderr = on_stderr
}
vim.fn.jobstart(args, params)
