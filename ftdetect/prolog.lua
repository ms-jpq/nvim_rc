vim.api.nvim_create_autocmd(
  {"BufNewFile", "BufRead"},
  {
    pattern = {"*.pl"},
    callback = function()
      vim.bo.filetype = "prolog"
    end
  }
)
