vim.api.nvim_create_autocmd(
  {"BufNewFile", "BufRead"},
  {
    pattern = {"*.ini"},
    callback = function()
      vim.bo.filetype = "cfg"
    end
  }
)
