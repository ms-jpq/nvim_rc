
# local go_replace = function ()

#   lv.op_go_replace = function (selec)
#     local r1, c1, r2, c2 = bindings.p_op_marks(selec)
#     r1, r2 = r1 - 1, r2 - 1
#     c1, c2 = c1 + 1, c2 + 1
#     local text = fn.getreg("*")
#     local lines = api.nvim_buf_get_lines(0, r1, r2 + 1, true)
#     local lst = r2 - r1 + 1
#     local lst_len = #lines[lst]
#     local pre = string.sub(lines[1], 1, c1 - 1)
#     local post = string.sub(lines[lst], math.min(c2 + 1, lst_len + 1), lst_len)
#     local replacement = pre .. text .. post
#     local new_lines = vim.split(replacement, "\n", true)
#     local len = #new_lines
#     if new_lines[len] == "" then
#       new_lines[len] = nil
#     end
#     api.nvim_buf_set_lines(0, r1, r2 + 1, true, new_lines)
#   end

#   bindings.map.normal("gr", "<cmd>set opfunc=v:lua.lv.op_go_replace<cr>g@")
#   bindings.map.visual("gr", "<esc><cmd>lua lv.op_go_replace()<cr>")


#   lv.op_go_replace_line = function ()
#     local r, _ = unpack(api.nvim_win_get_cursor(0))
#     r = r - 1
#     local replacement = fn.getreg("*")
#     local new_lines = vim.split(replacement, "\n", true)
#     local len = #new_lines
#     if new_lines[len] == "" then
#       new_lines[len] = nil
#     end
#     api.nvim_buf_set_lines(0, r, r + 1, true, new_lines)
#   end

#   bindings.map.normal("grr", "<cmd>lua lv.op_go_replace_line()<cr>")

# end
# registry.defer(go_replace)
