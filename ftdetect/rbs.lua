vim.api.nvim_create_autocmd(
  {"BufNewFile", "BufRead"},
  {
    pattern = {"*.rbs"},
    callback = function()
      vim.bo.syntax = "ruby"
    end
  }
)
