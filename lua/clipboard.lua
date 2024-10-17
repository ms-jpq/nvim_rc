local esc = "\027"
local sep = "\n"
local tmux = vim.env.TMUX
local ssh = vim.env.SSH_TTY

local osc52 = function(data)
  local acc = {}

  -- TMUX wrap start
  if tmux then
    table.insert(acc, esc .. "Ptmux;")
  end

  -- TMUX escape `esc`
  if tmux then
    table.insert(acc, esc)
  end

  -- OSC52 start
  table.insert(acc, esc .. "]52;c;")

  -- OSC52 body
  table.insert(acc, data)

  -- TMUX escape `esc`
  if tmux then
    table.insert(acc, esc)
  end

  -- OSC52 end
  table.insert(acc, esc .. [[\]])

  -- TMUX wrap end
  if tmux then
    table.insert(acc, esc .. [[\]])
  end

  return table.concat(acc, "")
end

local send = function(stdin, ...)
  vim.system({...}, {stdin = stdin})
end

local recv = function(text, ...)
  local proc = vim.system({...}, {text = text}):wait()
  return vim.split(proc.stdout, sep)
end

local copy = function(lines)
  local s = table.concat(lines, sep)

  if tmux then
    send(s, "tmux", "load-buffer", "--", "-")
  end

  if ssh then
    local b = vim.base64.encode(s)
    vim.api.nvim_chan_send(2, osc52(b))
  elseif vim.fn.has("mac") then
    send(s, "pbcopy")
  elseif vim.fn.has("unix") then
    send(s, "wl-copy")
  end
end

local paste = function()
  -- vim.api.nvim_chan_send(2, osc52("?"))
  if not ssh then
    if vim.fn.has("mac") then
      return recv(false, "pbpaste")
    elseif vim.fn.has("unix") then
      return recv(false, "wl-paste")
    elseif vim.fn.has("win32") then
      local pwsh = {
        "powershell.exe",
        "-NoProfile",
        "-Command",
        "Get-Clipboard"
      }
      return recv(true, unpack(pwsh))
    end
  end
  if tmux then
    return recv(false, "tmux", "save-buffer", "-")
  end
  return {}
end

vim.o.clipboard = "unnamedplus"
vim.g.clipboard = {
  name = "OSC 52",
  cache_enabled = true,
  copy = {
    ["+"] = copy,
    ["*"] = copy
  },
  paste = {
    ["+"] = paste,
    ["*"] = paste
  }
}

vim.paste = (function(paste)
  return function(lines, phase)
    local acc = {}
    for _, line in ipairs(lines) do
      for _, l in ipairs(vim.split(line, "\027%[27;5;106~")) do
        table.insert(acc, l)
      end
    end
    return paste(acc, phase)
  end
end)(vim.paste)
