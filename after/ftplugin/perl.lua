local shebang = [[#!]]
local line = unpack(vim.api.nvim_buf_get_lines(0, 0, 1, true))
if
  string.sub(line, 0, #shebang) == shebang and
    string.find(line, "swipl") ~= nil
 then
  vim.bo.filetype = "prolog"
end
