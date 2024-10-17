local copy = function(reg)
end

local paste = function(reg)
end

vim.g.clipboard = {
  name = "OSC 52",
  copy = {
    ["+"] = copy("+"),
    ["*"] = copy("*")
  },
  paste = {
    ["+"] = paste("+"),
    ["*"] = paste("*")
  }
}
