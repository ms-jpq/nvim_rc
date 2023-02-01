#!/usr/bin/env -S -- swipl
:- (initialization owo).
:- use_module(library(prolog_pack)).
owo() :-
    current_prolog_flag(os_argv, [_, A|_]),
    file_directory_name(A, B),
    file_directory_name(B, C),
    directory_file_path(C, lib, D),
    directory_file_path(D, prolog_ls, E),
    directory_file_path(E, lsp_server, F),
    set_prolog_flag(argv, [stdio]),
    current_prolog_flag(argv, G),
    writeln(G),
    pack_attach(F, []),
    use_module(library(lsp_server)),
    lsp_server:main,
    halt.
