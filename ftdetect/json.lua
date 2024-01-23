vim.filetype.add(
  {
    extension = {
      tfstate = "json"
    },
    filename = {
      [".swcrc"] = "json",
      ["terraform.tfstate.backup"] = "json"
    }
  }
)
