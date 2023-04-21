vim.filetype.add(
  {
    pattern = {
      [".*/git/.*config"] = "gitconfig",
      [".*/git/attributes"] = "gitattributes",
      [".*/git/ignore"] = "gitignore"
    }
  }
)
