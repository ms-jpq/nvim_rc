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

function Ndeps()
  call termopen([s:top_level . '/init.py', 'deps'])
endfunction
command! Ndeps call Ndeps()

call luaeval('require("_init")()', [])
