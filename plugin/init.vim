"autocmd BufReadPre,BufNewFile * let b:did_ftplugin = 1
command! -nargs=0 FTdetect filetype detect

function s:Ndeps()
  call termopen([stdpath('config') . '/init.py', 'deps'])
endfunction
command! Ndeps call s:Ndeps()
