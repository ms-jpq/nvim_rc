vim.filetype.add(
  {
    extension = {
      nspawn = "systemd"
    },
    pattern = {
      [".*/systemd/.*%.conf"] = "systemd"
    }
  }
)
