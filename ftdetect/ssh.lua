vim.filetype.add(
  {
    pattern = {
      [".*/ssh/.*%.conf"] = "sshconfig"
    }
  }
)
