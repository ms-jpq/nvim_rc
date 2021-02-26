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


function LVon_exit(_, code, __)
  call luaeval('lv.on_exit(...)', [a:code])
endfunction
function LVon_stdout(_, msg, __)
  call luaeval('lv.on_stdout(...)', [a:msg])
endfunction
function LVon_stderr(_, msg, __)
  call luaeval('lv.on_stderr(...)', [a:msg])
endfunction


let s:top_level = resolve(expand('<sfile>:p:h'))
call luaeval('require("init")(...)', [s:top_level])
