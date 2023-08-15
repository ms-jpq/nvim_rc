local buf = vim.api.nvim_get_current_buf()
vim.schedule(
  function()
    vim.api.nvim_buf_set_option(buf, "syntax", "ruby")
  end
)
