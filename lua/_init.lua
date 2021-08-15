return function()
  local cwd = vim.fn.stdpath("config")

  local on_exit = function(_, code)
    if code ~= 143 then
      vim.api.nvim_err_writeln(" | EXITED - " .. code)
    end
  end

  local on_stdout = function(_, msg)
    vim.api.nvim_out_write(table.concat(msg, "\n"))
  end

  local on_stderr = function(_, msg)
    vim.api.nvim_err_write(table.concat(msg, "\n"))
  end

  local main = function ()
    local vpy = cwd .. "/.vars/runtime/bin/python3"
    if vim.fn.filereadable(vpy) == 1 then
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
    vim.v.servername
  }
  local params = {
    cwd = cwd,
    on_exit = on_exit,
    on_stdout = on_stdout,
    on_stderr = on_stderr
  }
  vim.fn.jobstart(args, params)
end
