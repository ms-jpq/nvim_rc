local ftdetect = function(filename, bufnr)
  local lhs = [[#!/usr/bin/env ]]
  local l1 = unpack(vim.api.nvim_buf_get_lines(bufnr, 0, 1, true))
  if not vim.startswith(l1, lhs) then
    return
  else
    local rhs = string.sub(l1, #lhs + 1)
    local matches = {
      haskell = "run(ghc|haskell)|stack",
      javascript = "node",
      perl = "perl",
      prolog = "swipl",
      python = "python3?",
      r = "Rscript",
      ruby = "ruby",
      sh = "(pw)@<!(ba|z)?sh"
    }

    for ft, pattern in pairs(matches) do
      local pat = [[\v^.{-}]] .. pattern .. ".{-}$"
      if #vim.fn.matchstr(rhs, pat) > 1 then
        return ft
      end
    end

    return vim.filetype.match({filename = filename})
  end
end
vim.filetype.add {
  pattern = {
    ["[^.]*"] = {
      priority = -math.huge,
      ftdetect
    }
  },
  extension = {
    cgi = ftdetect
  }
}
