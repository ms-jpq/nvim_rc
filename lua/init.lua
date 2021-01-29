return function(args)
  local cwd = unpack(args)

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

  local main = function ()
    local vpy = cwd .. "/.vars/runtime/bin/python3"
    if vim.api.nvim_call_function("filereadable", {vpy}) == 1 then
      return vpy
    else
      return "python3"
    end
  end

  local args = {
    main(),
    "-m",
    "python",
    "run",
    "--socket",
    vim.api.nvim_get_vvar("servername")
  }
  local params = {
    cwd = cwd,
    on_exit = "LVon_exit",
    on_stdout = "LVon_stdout",
    on_stderr = "LVon_stderr"
  }
  vim.api.nvim_call_function("jobstart", {args, params})
end
