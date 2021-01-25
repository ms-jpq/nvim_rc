local nvim_home = vim.api.nvim_list_runtime_paths()[1]
local py_main = "python"

lv = lv or {}
lv.on_exit = function(args)
  local code = unpack(args)
  vim.api.nvim_err_writeln(" | EXITED - " .. code)
end

lv.on_stdout = function(args)
  local msg = unpack(args)
  vim.api.nvim_out_write(table.concat(msg, "\n"))
end

lv.on_stderr = function(args)
  local msg = unpack(args)
  vim.api.nvim_err_write(table.concat(msg, "\n"))
end

local args = {"python3", "-m", py_main, "run", "--socket", vim.api.nvim_get_vvar("servername")}
local params = {
  cwd = nvim_home,
  on_exit = "LVon_exit",
  on_stdout = "LVon_stdout",
  on_stderr = "LVon_stderr"
}
vim.api.nvim_call_function("jobstart", {args, params})
