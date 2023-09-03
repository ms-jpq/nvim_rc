vim.filetype.add(
  {
    extension = {
      env = "env",
      var = "env"
    },
    filename = {
      [".env"] = "env"
    },
    pattern = {
      [".*/etc/default/.*"] = "env"
    }
  }
)
