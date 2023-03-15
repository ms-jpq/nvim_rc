vim.filetype.add(
  {
    extension = {
      nspawn = "systemd",
      service = "systemd",
      socket = "systemd",
      netdev = "systemd"
    },
    pattern = {
      [".*/systemd/.*%.conf"] = "systemd"
    }
  }
)
