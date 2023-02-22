vim.filetype.add(
  {
    pattern = {
      [".*/systemd/.*%.conf"] = "systemd"
    }
  }
)
