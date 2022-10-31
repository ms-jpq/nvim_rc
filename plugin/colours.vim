set background=light

function s:colours()
  highlight Normal   guibg=NONE ctermbg=NONE
  highlight NormalNC guibg=NONE ctermbg=NONE
endfunction

autocmd auto ColorScheme * call s:colours()
