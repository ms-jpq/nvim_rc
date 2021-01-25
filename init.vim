nnoremap <silent> Q  <esc>
nnoremap <silent> QQ <cmd>quitall!<cr>
vnoremap <silent> Q  <nop>
vnoremap <silent> QQ <cmd>quitall!<cr>

filetype on
set nomodeline
set secure
set termguicolors
set shortmess+=I


function LVon_exit(_, code, __)
  call luaeval('lv.on_exit(...)', [a:code])
endfunction
function LVon_stdout(_, msg, __)
  call luaeval('lv.on_stdout(...)', [a:msg])
endfunction
function LVon_stderr(_, msg, __)
  call luaeval('lv.on_stderr(...)', [a:msg])
endfunction


lua require 'init'