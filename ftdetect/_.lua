local ftdetect = function(filename, bufnr)
  local lhs = [[#!/usr/bin/env ]]
  local l1 = unpack(vim.api.nvim_buf_get_lines(bufnr, 0, 1, true))
  if not vim.startswith(l1, lhs) then
    return
  else
    local rhs = string.sub(l1, #lhs + 1)
    local matches = {
      sh = "(pw)@<!(ba|z)?sh",
      python = "python3?",
      perl = "perl",
      ruby = "ruby",
      r = "Rscript",
      prolog = "swipl"
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
