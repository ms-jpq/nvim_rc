(function(ns, cb)
  -- TODO: https://github.com/neovim/neovim/pull/13896
  local function range_from_selection()
    -- [bufnum, lnum, col, off]; both row and column 1-indexed
    local start = vim.fn.getpos("v")
    local end_ = vim.fn.getpos(".")
    local start_row = start[2]
    local start_col = start[3]
    local end_row = end_[2]
    local end_col = end_[3]

    -- A user can start visual selection at the end and move backwards
    -- Normalize the range to start < end
    if start_row == end_row and end_col < start_col then
      end_col, start_col = start_col, end_col
    elseif end_row < start_row then
      start_row, end_row = end_row, start_row
      start_col, end_col = end_col, start_col
    end

    return {{start_row, start_col - 1}, {end_row, end_col - 1}}
  end

  local cancel = function()
  end

  local error_codes = vim.lsp.protocol.ErrorCodes
  local ignored_codes = {
    [error_codes.ContentModified] = true,
    [error_codes.InternalError] = true,
    [error_codes.MethodNotFound] = true,
    [error_codes.RequestCancelled] = true
  }

  local callback = function(idx, row, error, resp)
    local err_code = (error or {}).code
    if not ignored_codes[err_code] then
      local actionable = (function()
        local acc = {}
        for key, val in pairs(resp or {}) do
          table.insert(acc, {key, val})
          break
        end
        return #acc > 0
      end)()
      _G[ns][cb](idx, row, error or vim.NIL, actionable)
    end
  end

  _G[ns].code_action = function(idx)
    local params = (function()
      local mode = vim.api.nvim_get_mode().mode
      if mode == "v" or mode == "V" then
        return vim.lsp.util.make_given_range_params(
          unpack(range_from_selection())
        )
      else
        return vim.lsp.util.make_range_params()
      end
    end)()
    params.context = {diagnostics = vim.lsp.diagnostic.get_line_diagnostics()}

    local buf = vim.api.nvim_get_current_buf()
    local clients = vim.lsp.get_active_clients({bufnr = buf})
    local row = unpack(vim.api.nvim_win_get_cursor(0))
    row = row - 1

    cancel()

    local cancels = {}
    for _, client in pairs(clients) do
      local go, handle =
        client.request(
        "textDocument/codeAction",
        params,
        function(error, resp)
          callback(idx, row, error, resp)
        end,
        buf
      )
      if go then
        table.insert(
          cancels,
          function()
            client.cancel_request(handle)
          end
        )
      end
    end
    cancel = function()
      for _, handle in pairs(cancels) do
        handle()
      end
    end
  end
end)(...)
