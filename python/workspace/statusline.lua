(function ()
  local lsp_clients = function ()
    local clients = vim.lsp.buf_get_clients(0)
    local acc = {}
    for _, client in ipairs(clients) do
      local warnings = vim.lsp.diagnostic.get_count(0, "Warning", client.id)
      local errors = vim.lsp.diagnostic.get_count(0, "Error", client.id)
      table.insert(acc, {name=client.name, warnings=warnings, errors=errors})
    end
    return acc
  end

  LUA_status_line = function ()
    return
  end
end)()
