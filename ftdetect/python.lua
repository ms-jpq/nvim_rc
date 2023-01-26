vim.filetype.add {
  pattern = {
    [".*"] = {
      priority = -math.huge,
      function(_, bufnr)
        local l1 = vim.filetype.getlines(bufnr, 1)
        local match_1 = vim.fn.matchstr(l1, [[\V\^#!/usr/bin/env]])
        local match_2 = vim.fn.matchstr(l1, [[\v.*python3?.*]])

        if #match_1 > 1 and #match_2 > 1 then
          return "sh"
        end
      end
    }
  }
}
