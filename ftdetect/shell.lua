vim.filetype.add {
  pattern = {
    [".*"] = {
      priority = -math.huge,
      function(_, bufnr)
        local content = vim.filetype.getlines(bufnr, 1)
        if
          vim.filetype.matchregex(content, [[^#!/usr/bin/env -S -- (ba|z)sh.*]])
         then
          return "sh"
        end
      end
    }
  }
}
