local t1 = vim.fn.localtime()
local cwd = vim.fn.stdpath("config")

local l1 = function()
  vim.opt.loadplugins = false
  vim.opt.modeline = false
  vim.opt.secure = true
  vim.opt.termguicolors = true
end

local l2 = function()
  vim.api.nvim_set_keymap("n", "q", "<nop>", {noremap = true})
  vim.api.nvim_set_keymap("n", "Q", "<esc>", {noremap = true})
  vim.api.nvim_set_keymap("n", "QQ", "<cmd>quitall!<cr>", {noremap = true})
  vim.api.nvim_set_keymap("v", "QQ", "<cmd>quitall!<cr>", {noremap = true})
  vim.api.nvim_set_keymap("v", "Q", "<nop>", {noremap = true})
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
      vim.fn.termopen({vim.fn.stdpath("config") .. "/init.py", "deps"})
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
    local vpy = cwd .. "/tmp/runtime/bin/python3"
    if vim.fn.filereadable(vpy) == 1 then
      return vpy
    else
      return "python3"
    end
  end

  local args = {
    main(),
    "-u",
    "-m",
    "python",
    "run",
    "--ppid",
    vim.fn.getpid(),
    "--socket",
    vim.v.servername
  }
  local params = {
    cwd = cwd,
    on_exit = on_exit,
    on_stdout = on_stdout,
    on_stderr = on_stderr,
    env = {_VIM_START_TIME = tostring(t1)}
  }
  vim.fn.jobstart(args, params)
end

l4 = function()
  local man = unpack(vim.api.nvim_get_runtime_file("plugin/man.*", true))
  vim.cmd("source " .. man)
  vim.g.omni_sql_no_default_maps = 1
end

l1()
l2()
l3()
l4()
