(function()
  local cache = function(f)
    local ans = nil
    local w = 0
    local count = 0

    return function(...)
      local win = vim.api.nvim_get_current_win()
      if win ~= w or count % 15 == 0 then
        ans = f(...)
      end
      w = win
      count = count + 1
      return ans
    end
  end

  local lsp = function()
    local buf = vim.api.nvim_get_current_buf()

    local names =
      (function()
      local clients = vim.lsp.buf_get_clients(buf)
      local acc = {}
      for _, client in pairs(clients) do
        table.insert(acc, client.name)
      end
      table.sort(
        acc,
        function(lhs, rhs)
          return vim.stricmp(lhs, rhs) < 0
        end
      )
      return acc
    end)()

    local warnings =
      #vim.diagnostic.get(buf, {severity = vim.diagnostic.severity.WARN})
    local errors =
      #vim.diagnostic.get(buf, {severity = vim.diagnostic.severity.ERROR})

    local s1 = #names > 0 and "[" .. table.concat(names, " ") .. "]" or ""
    local s2 = warnings > 0 and " ⚠️  " .. warnings or ""
    local s3 = errors > 0 and " ⛔️ " .. errors or ""

    return s1 .. s2 .. s3
  end

  LSP_status_line = cache(lsp)
end)()
