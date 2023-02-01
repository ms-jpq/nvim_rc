#!/usr/bin/env -S -- swipl

:- initialization(owo).
:- use_module(library(prolog_pack)).

owo() :-
    current_prolog_flag(os_argv, [_, Arg0|_]),
    file_directory_name(Arg0, Parent),
    file_directory_name(Parent, GrandParent),
    directory_file_path(GrandParent, 'lib', Lib),
    directory_file_path(Lib, 'prolog_ls', PrologLS),
    directory_file_path(PrologLS, 'lsp_server', LSP),

    set_prolog_flag(argv, [stdio]),
    current_prolog_flag(argv, ArgV),
    writeln(ArgV),
    pack_attach(LSP, []),
    use_module(library(lsp_server)),
    lsp_server:main,
    halt.
