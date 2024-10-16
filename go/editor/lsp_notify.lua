(function(eol)
  vim.validate {eol = {eol, "string"}}
  local method = vim.lsp.protocol.Methods.textDocument_didChange
  local buf = vim.api.nvim_get_current_buf()
  local clients = vim.lsp.get_clients({bufnr = buf, method = method})
  local uri = vim.uri_from_bufnr(buf)

  local error_codes = vim.lsp.protocol.ErrorCodes
  local ignored_codes = {
    -- [error_codes.InternalError] = true,
    -- [error_codes.InvalidRequest] = true,
    [error_codes.MethodNotFound] = true
  }

  local text = table.concat(vim.api.nvim_buf_get_lines(buf, 0, -1, true), eol)
  local params = {
    {
      textDocument = {
        uri = uri,
        version = vim.lsp.util.buf_versions[buf]
      },
      contentChanges = {{text = text}}
    }
  }
  for _, client in pairs(clients) do
    -- client.notify(
    --   method,
    --   params,
    --   function(error, resp)
    --     local err_code = (error or {}).code
    --     if not ignored_codes[err_code] then
    --       vim.print {error = error, params = params, resp = resp}
    --     end
    --   end,
    --   buf
    -- )
  end
end)(...)
