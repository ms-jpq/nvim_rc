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
  end
end

local paste = function(reg)
  local clipboard = reg == "+" and "c" or "p"
  return function(lines)
    local s = table.concat(lines, "\n")
    -- vim.api.nvim_chan_send(2, osc52(clipboard, s))
  end
end

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
