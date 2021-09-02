command! -nargs=0 FTdetect filetype detect

function s:Ndeps()
  call termopen([stdpath('config') . '/init.py', 'deps'])
endfunction
command! Ndeps call s:Ndeps()

augroup man
  autocmd!
  autocmd BufReadCmd man://* call man#read_page(matchstr(expand('<amatch>'), 'man://\zs.*'))
augroup END

