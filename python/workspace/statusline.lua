(function ()
  local cache = function (f)
    local ans = nil
    local w = 0
    local count = 0

    return function ()
      local win = vim.api.nvim_get_current_win()
      if win ~= w or count % 15 == 0 then
        ans = f()
      end
      w = win
      count = count + 1
      return ans
    end
  end


  local lsp = function ()
    local clients = vim.lsp.buf_get_clients(0)
    local names = {}
    local warnings, errors = 0, 0

    for _, client in pairs(clients) do
      warnings = warnings + vim.lsp.diagnostic.get_count(0, "Warning", client.id)
      errors = errors + vim.lsp.diagnostic.get_count(0, "Error", client.id)
      table.insert(names, client.name)
    end

    local s1 = #names ~= 0 and "[" .. table.concat(names, " ") .. "]" or ""
    local s2 = warnings ~= 0 and " ⚠️  " .. warnings or ""
    local s3 = errors ~= 0 and " ⛔️ " .. errors or ""

    return s1 .. s2 .. s3
  end

  LSP_status_line = cache(lsp)
end)()
