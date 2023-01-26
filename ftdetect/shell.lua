vim.filetype.add {
  pattern = {
    [".*"] = {
      priority = -math.huge,
      function(_, bufnr)
        local l1 = vim.filetype.getlines(bufnr, 1)
        local match =
          vim.fn.matchstr(l1, [[\V\^#!/usr/bin/env -S -- \(ba\|z\)\?sh\.\*]])

        if #match > 1 then
          return "sh"
        end
      end
    }
  }
}
