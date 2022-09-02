vim.api.nvim_create_autocmd(
  {"BufNewFile", "BufRead"},
  {
    pattern = {"*.cts", "*.mts"},
    callback = function()
      vim.bo.filetype = "typescript"
    end
  }
)
