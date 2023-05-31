set background=light

function s:colours()
  highlight! Normal     guibg=NONE ctermbg=NONE
  highlight! NormalNC   guibg=NONE ctermbg=NONE
  highlight! link MatchParen Cursor
endfunction

autocmd ColorScheme * call s:colours()
