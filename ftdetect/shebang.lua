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
          if #vim.fn.matchstr(rhs, [[\v.*(ba|z)?sh.*]]) > 1 then
            return "sh"
          elseif #vim.fn.matchstr(rhs, [[\v.*python3?.*]]) > 1 then
            return "python"
          end
        end
      end
    }
  }
}
