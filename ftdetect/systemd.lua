vim.filetype.add(
  {
    extension = {
      nspawn = "systemd",
      service = "systemd"
    },
    pattern = {
      [".*/systemd/.*%.conf"] = "systemd"
    }
  }
)
