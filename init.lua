local is_win = vim.fn.has("win32") == 1
local t1 = vim.fn.localtime()
local cwd = vim.fn.stdpath("config")
local py = is_win and "python.exe" or "/usr/bin/python3"

local l1 = function()
  vim.opt.loadplugins = false
  vim.opt.modeline = false
  vim.opt.secure = true
  vim.opt.termguicolors = true
  vim.g.python3_host_prog = py
end

local l2 = function()
  for _, mode in pairs({"n", "v"}) do
    vim.api.nvim_set_keymap(mode, "Q", "<nop>", {noremap = true})
    vim.api.nvim_set_keymap(mode, "QQ", "<cmd>quitall!<cr>", {noremap = true})
  end
  vim.opt.shortmess:append("I")

  vim.api.nvim_create_user_command(
    "FTdetect",
    function()
      vim.cmd [[filetype detect]]
    end,
    {}
  )
  vim.api.nvim_create_user_command(
    "Ndeps",
    function()
      vim.fn.termopen(
        {
          "gmake",
          "--directory",
          vim.fn.stdpath("config"),
          "--always-make",
          "--",
          "mvp"
        }
      )
    end,
    {}
  )
end

local l3 = function()
  local linesep = "\n"

  local on_exit = function(_, code)
    if code ~= 143 then
      vim.api.nvim_err_writeln("EXITED - " .. code)
    end
  end

  local on_stdout = function(_, msg)
    vim.api.nvim_out_write(table.concat(msg, linesep))
  end

  local on_stderr = function(_, msg)
    vim.api.nvim_echo({{table.concat(msg, linesep), "ErrorMsg"}}, true, {})
  end

  local main = function()
    local vpy = (function()
      local py2 = is_win and "python.exe" or "python3"
      if is_win then
        return cwd .. "/var/runtime/Scripts/" .. py2
      else
        return cwd .. "/var/runtime/bin/" .. py2
      end
    end)()
    if vim.fn.filereadable(vpy) == 1 then
      return vpy
    else
      return py
    end
  end

  local srv = is_win and {"localhost:0"} or {}
  local server = vim.fn.serverstart(unpack(srv))

  local args = {
    main(),
    "-s",
    "-u",
    "-m",
    "go",
    "run",
    "--ppid",
    vim.fn.getpid(),
    "--socket",
    server
  }
  local params = {
    cwd = cwd,
    on_exit = on_exit,
    on_stdout = on_stdout,
    on_stderr = on_stderr,
    env = {
      _VIM_START_TIME = tostring(t1),
      PYTHONSAFEPATH = "1",
      PYTHONPATH = cwd
    }
  }
  vim.fn.jobstart(args, params)
end

local l4 = function()
  vim.g.no_plugin_maps = 1

  local man = unpack(vim.api.nvim_get_runtime_file("plugin/man.*", true))
  vim.cmd("source " .. man)

  vim.cmd("source " .. cwd .. "/plugin/theme.vim")

  local parens =
    unpack(vim.api.nvim_get_runtime_file("plugin/matchparen.vim", true))
  vim.cmd("source " .. parens)
end

l1()
l2()
l3()
l4()
