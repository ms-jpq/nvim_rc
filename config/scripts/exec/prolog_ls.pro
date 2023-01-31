#!/usr/bin/env -S -- swipl

:- initialization(main, main).
:- use_module(library(prolog_pack)).

main(_Argv) :-
    current_prolog_flag(os_argv, [_, Arg0|_]),
    file_directory_name(Arg0, Parent),
    file_directory_name(Parent, GrandParent),
    directory_file_path(GrandParent, 'lib', Lib),
    directory_file_path(Lib, 'prolog_ls', PrologLS),
    directory_file_path(PrologLS, 'lsp_server', LSP),

    pack_attach(LSP, []),
    lsp_server:main,

    halt.
