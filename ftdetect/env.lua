vim.filetype.add(
  {
    extension = {
      env = "env"
    },
    filename = {
      [".env"] = "env"
    },
    pattern = {
      [".*/etc/default/.*"] = "env",
    }
  }
)
