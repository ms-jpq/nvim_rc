set background=light

function s:colours()
  highlight! CursorLine        guibg=#eae0f1 ctermbg=253
  highlight! EndOfBuffer       guibg=NONE    ctermbg=NONE
  highlight! Normal            guibg=NONE    ctermbg=NONE
  highlight! NormalNC          guibg=NONE    ctermbg=NONE
  highlight! SignColumn        guibg=NONE    ctermbg=NONE
  highlight! TreesitterContext guibg=#C5DFEA ctermbg=254
  highlight! VertSplit         guibg=NONE    ctermbg=NONE
  highlight! link              CursorColumn  CursorLine
  highlight! link              MatchParen    Search
  highlight! link              WinSeparator  LineNr
endfunction

autocmd ColorScheme * call s:colours()
