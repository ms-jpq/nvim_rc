(function()
  Go.move = function(key, shift)
    local win = vim.api.nvim_get_current_win()
    local row, _ = unpack(vim.api.nvim_win_get_cursor(win))
    local next = row + shift

    local thisf = vim.fn.foldlevel(row)
    local nextf = vim.fn.foldlevel(next)

    if thisf < nextf then
      vim.cmd(next .. [[foldopen]])
    elseif thisf > nextf then
      local foldlvl = vim.wo[win].foldlevel
      if thisf > foldlvl then
        vim.cmd(row .. [[foldclose]])
      end
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
