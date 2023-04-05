(function()
  local systemd = "systemd"
  vim.filetype.add(
    {
      extension = {
        container = systemd,
        netdev = systemd,
        netdev = systemd,
        network = systemd,
        nspawn = systemd,
        service = systemd,
        socket = systemd
      },
      pattern = {
        [".*/systemd/.*%.conf"] = systemd
      }
    }
  )
end)()
