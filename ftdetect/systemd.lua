vim.filetype.add(
  {
    extension = {
      nspawn = "systemd",
      service = "systemd",
      socket = "systemd"
    },
    pattern = {
      [".*/systemd/.*%.conf"] = "systemd"
    }
  }
)
