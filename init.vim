nnoremap <silent> q  <nop>
nnoremap <silent> Q  <esc>
nnoremap <silent> QQ <cmd>quitall!<cr>
vnoremap <silent> Q  <nop>
vnoremap <silent> QQ <cmd>quitall!<cr>

"autocmd BufReadPre,BufNewFile * let b:did_ftplugin = 1
command! -nargs=0 FTdetect filetype detect
filetype on
set nomodeline
set secure
set termguicolors
set shortmess+=I
set commentstring=#\ %s

function s:Ndeps()
  call termopen([stdpath('config') . '/init.py', 'deps'])
endfunction
command! Ndeps call s:Ndeps()

call luaeval('require("_init")()', [])
