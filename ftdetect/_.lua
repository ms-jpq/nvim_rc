vim.filetype.add {
  pattern = {
    [".*"] = {
      priority = -math.huge,
      function(filename, bufnr)
        local filetype = vim.filetype.match({filename = filename})
        if filetype then
          return filetype
        else
          local lhs = [[#!/usr/bin/env ]]
          local l1 = vim.filetype.getlines(bufnr, 1)
          if not vim.startswith(l1, lhs) then
            return
          else
            local rhs = string.sub(l1, #lhs + 1)
            local matches = {
              sh = "(pw)@<!(ba|z)?sh",
              python = "python3?",
              perl = "perl",
              ruby = "ruby",
              r = "Rscript"
            }
            for ft, pattern in pairs(matches) do
              local pat = [[\v^.{-}]] .. pattern .. ".{-}$"
              if #vim.fn.matchstr(rhs, pat) > 1 then
                return ft
              end
            end
          end
        end
      end
    }
  }
}
