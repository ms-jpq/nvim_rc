let g:omni_sql_no_default_maps = 1

command! -nargs=0 FTdetect filetype detect

function s:Ndeps()
  call termopen([stdpath('config') . '/init.py', 'deps'])
endfunction
" TODO -- nvim_add_user_command
command! Ndeps call s:Ndeps()

command! -bang -bar -addr=other -complete=customlist,man#complete -nargs=* Man
      \ if <bang>0 | call man#init_pager() |
      \ else | call man#open_page(<count>, <q-mods>, <f-args>) | endif

augroup man
  autocmd!
  autocmd BufReadCmd man://* call man#read_page(matchstr(expand('<amatch>'), 'man://\zs.*'))
augroup END

