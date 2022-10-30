(function(ns, cb)
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
  local callback = _G[ns][cb]

  _G[ns].code_action = function()
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

    cancel()
    cancel =
      vim.lsp.buf_request_all(
      vim.api.nvim_get_current_buf(),
      "textDocument/codeAction",
      params,
      callback
    )
  end
end)(...)
