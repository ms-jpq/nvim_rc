# local bindings = require "libs/bindings"
# local registry = require "libs/registry"
# local std = require "libs/std"


# --#################### Cursors Region ####################

# local select_visual = function (r1, c1, r2, c2)
#   fn.setpos("'<", {0, r1, c1 + 1, 0})
#   fn.setpos("'>", {0, r2, c2 + 1, 0})
# end


# lv.move_up = function ()
#   if not vim.bo.modifiable then
#     return
#   end

#   local r, c = unpack(api.nvim_win_get_cursor(0))
#   if r <= 1 then
#     return
#   end
#   r = r - 1
#   local curr = api.nvim_buf_get_lines(0, r, r + 1, true)
#   local nxt  = api.nvim_buf_get_lines(0, r - 1, r, true)
#   local new = std.concat{curr, nxt}
#   api.nvim_buf_set_lines(0, r - 1, r + 1, true, new)
#   api.nvim_win_set_cursor(0, {r, c})
# end


# lv.move_down = function ()
#   if not vim.bo.modifiable then
#     return
#   end

#   local r, c = unpack(api.nvim_win_get_cursor(0))
#   if r >= api.nvim_buf_line_count(0) then
#     return
#   end
#   r = r - 1
#   local curr = api.nvim_buf_get_lines(0, r, r + 1, true)
#   local nxt  = api.nvim_buf_get_lines(0, r + 1, r + 2, true)
#   local new = std.concat{nxt, curr}
#   api.nvim_buf_set_lines(0, r, r + 2, true, new)
#   api.nvim_win_set_cursor(0, {r + 2, c})
# end


# local reselect_visual = function ()
#   bindings.exec[[norm! gv]]
# end


# lv.move_v_up = function ()
#   if not vim.bo.modifiable then
#     return
#   end

#   local r1, c1, r2, c2 = bindings.p_op_marks()
#   if r1 <= 1 then
#     reselect_visual()
#     return
#   end
#   r1, r2 = r1 - 1, r2 - 1

#   local curr = api.nvim_buf_get_lines(0, r1, r2 + 1, true)
#   local nxt  = api.nvim_buf_get_lines(0, r1 - 1, r1, true)
#   local new = std.concat{curr, nxt}
#   api.nvim_buf_set_lines(0, r1 - 1, r2 + 1, true, new)

#   select_visual(r1, c1, r2, c2)
#   reselect_visual()
# end


# lv.move_v_down = function ()
#   if not vim.bo.modifiable then
#     return
#   end

#   local r1, c1, r2, c2 = bindings.p_op_marks()
#   if r2 >= api.nvim_buf_line_count(0) then
#     reselect_visual()
#     return
#   end
#   r1, r2 = r1 - 1, r2 - 1

#   local curr = api.nvim_buf_get_lines(0, r1, r2 + 1, true)
#   local nxt  = api.nvim_buf_get_lines(0, r2 + 1, r2 + 2, true)
#   local new = std.concat{nxt, curr}
#   api.nvim_buf_set_lines(0, r1, r2 + 2, true, new)

#   select_visual(r1 + 2, c1, r2 + 2, c2)
#   reselect_visual()
# end


# -- drag regions around
# local vim_move = function ()

#   bindings.map.normal("<m-up>",   "<cmd>lua lv.move_up()<cr>")
#   bindings.map.normal("<m-down>", "<cmd>lua lv.move_down()<cr>")

#   bindings.map.visual("<m-up>",   "<esc><cmd>lua lv.move_v_up()<cr>")
#   bindings.map.visual("<m-down>", "<esc><cmd>lua lv.move_v_down()<cr>")

# end
# registry.defer(vim_move)

