local cfg = "cfg"
vim.filetype.add(
  {
    filename = {
      [".wslconfig"] = cfg,
      ["wsl.conf"] = cfg
    }
  }
)
