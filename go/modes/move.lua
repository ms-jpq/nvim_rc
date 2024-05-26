(function()
  Go.move = function(key, shift)
    local row, _ = unpack(vim.api.nvim_win_get_cursor(0))
    local next = row + shift

    local thisf = vim.fn.foldlevel(row)
    local nextf = vim.fn.foldlevel(next)

    if thisf < nextf then
      vim.cmd(next .. [[foldopen]])
    elseif thisf > nextf then
      vim.cmd(row .. [[foldclose]])
    end

    return (function()
      local count = vim.v.count
      if count ~= 0 then
        return "m'" .. count .. key
      else
        return "g" .. key
      end
    end)()
  end
end)()
