
# local magic_escape = function (word)
#   local escaped = fn.escape(word, [[/\]])
#   return [[\V]] .. string.gsub(escaped, "\n", [[\n]])
# end


# -- find selection
# local find = function ()

#   local hlselect = function (text)
#     fn.setreg("/", magic_escape(text))
#     bindings.exec[[set hlsearch]]
#   end

#   local selecthl = function (selc)
#     local selection = p_selection(selc)
#     hlselect(selection)
#     return selection
#   end

#   lv.op_search = function (selc)
#     selecthl(selc)
#   end

#   lv.op_fzf = function (selc)
#     local selection = selecthl(selc)
#     bindings.exec("BLines " .. selection)
#   end

#   lv.op_rg = function (selc)
#     local selection = selecthl(selc)
#     bindings.exec("Rg " .. selection)
#   end

#   bindings.map.normal("gs", "<cmd>set opfunc=v:lua.lv.op_search<cr>g@")

#   bindings.map.normal("gf", "<cmd>set opfunc=v:lua.lv.op_fzf<cr>g@")
#   bindings.map.normal("gF", "<cmd>set opfunc=v:lua.lv.op_rg<cr>g@")

#   bindings.map.visual("gf", "<esc><cmd>lua lv.op_fzf()<cr>")
#   bindings.map.visual("gF", "<esc><cmd>lua lv.op_rg()<cr>")

# end
# registry.defer(find)


# -- replace selection
# local replace = function ()

#   lv.op_sd = function (selc)
#     local selection = p_selection(selc)
#     local escaped = magic_escape(selection)
#     -- no magic
#     local input = [[:%s/]] .. escaped .. "//g<left><left>"
#     api.nvim_input(input)
#   end

#   -- no magic
#   bindings.map.normal("gt", "<cmd>set opfunc=v:lua.lv.op_sd<cr>g@")
#   bindings.map.visual("gt", "<ESC>:lua lv.op_sd()<cr>")
#   -- very magic
#   bindings.map.normal("gT", [[:%s/\v//g<left><left><left>]], {silent = false})

# end
# registry.defer(replace)
