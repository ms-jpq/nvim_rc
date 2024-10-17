local esc = "\027"
local tmux = vim.env.TMUX

local osc52 = function(clipboard, str)
  local b = vim.base64.encode(str)
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
  table.insert(acc, esc .. "]52;")
  table.insert(acc, clipboard)
  table.insert(acc, ";")

  -- OSC52 body
  table.insert(acc, b)

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

local copy = function(reg)
  local clipboard = reg == "+" and "c" or "p"
  return function(lines)
    local s = table.concat(lines, "\n")
    vim.api.nvim_chan_send(2, osc52("c", s))
    if tmux then
      vim.system({"tmux", "load-buffer", "--", "-"}, {stdin = lines})
    end
  end
end

local paste = function(reg)
  return function()
    -- vim.api.nvim_chan_send(2, osc52(clipboard, s))
    return vim.split("", "\n", {plain = true})
  end
end

vim.o.clipboard = "unnamedplus"
vim.g.clipboard = {
  name = "OSC 52",
  cache_enabled = true,
  copy = {
    ["+"] = copy("+"),
    ["*"] = copy("*")
  },
  paste = {
    ["+"] = paste("+"),
    ["*"] = paste("*")
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
