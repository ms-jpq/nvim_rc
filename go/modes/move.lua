(function()
  Go.move = function(key)
    local count = vim.v.count
    vim.cmd [[silent! foldopen]]
    if count ~= 0 then
      return "m'" .. count .. key
    else
      return "g" .. key
    end
  end
end)()
