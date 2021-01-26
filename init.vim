nnoremap <silent> Q  <esc>
nnoremap <silent> QQ <cmd>quitall!<cr>
vnoremap <silent> Q  <nop>
vnoremap <silent> QQ <cmd>quitall!<cr>

filetype on
set nomodeline
set secure
set termguicolors
set shortmess+=I


let s:top_level = resolve(expand('<sfile>:p:h'))
call luaeval('require("init")(...)', [s:top_level])
