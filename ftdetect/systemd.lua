local systemd = "systemd"
vim.filetype.add(
  {
    extension = {
      automount = systemd,
      container = systemd,
      mount = systemd,
      netdev = systemd,
      network = systemd,
      nspawn = systemd,
      service = systemd,
      socket = systemd
    },
    pattern = {
      [".*/.*%.service.d/.*%.conf"] = systemd,
      [".*/repart.d/.*%.conf"] = systemd,
      [".*/systemd/.*%.conf"] = systemd
    }
  }
)
