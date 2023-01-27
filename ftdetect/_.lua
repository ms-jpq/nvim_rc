vim.filetype.add {
  pattern = {
    [".*"] = {
      priority = -math.huge,
      function(_, bufnr)
        local lhs = [[#!/usr/bin/env]]
        local l1 = vim.filetype.getlines(bufnr, 1)
        if not vim.startswith(l1, lhs) then
          return
        else
          local rhs = string.sub(l1, #lhs + 1)
          local matches = {
            sh = [[\v.*(ba|z)?sh.*]],
            python = [[\v.*python3?.*]],
            perl = [[\v.*perl.*]],
          }
          for ft, pattern in pairs(matches) do
            if #vim.fn.matchstr(rhs, pattern) > 1 then
              return ft
            end
          end
        end
      end
    }
  }
}
