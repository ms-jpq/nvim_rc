local systemd = "systemd"
vim.filetype.add(
  {
    extension = {
      container = systemd,
      netdev = systemd,
      network = systemd,
      nspawn = systemd,
      service = systemd,
      socket = systemd
    },
    pattern = {
      [".*/repart.d/.*%.conf"] = systemd,
      [".*/systemd/.*%.conf"] = systemd
    }
  }
)
