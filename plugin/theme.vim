set background=light

function s:colours()
  highlight! Normal      guibg=NONE ctermbg=NONE
  highlight! NormalNC    guibg=NONE ctermbg=NONE
  highlight! SignColumn  guibg=NONE ctermbg=NONE
  highlight! EndOfBuffer guibg=NONE ctermbg=NONE
  highlight! VertSplit   guibg=NONE ctermbg=NONE
  highlight! link WinSeparator LineNr
  highlight! link MatchParen   Cursor
endfunction

autocmd ColorScheme * call s:colours()
