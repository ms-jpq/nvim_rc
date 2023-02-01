#!/usr/bin/env -S -- swipl
:- (initialization main).
main(_) :-
    current_prolog_flag(os_argv, [_, A|_]),
    file_directory_name(A, B),
    file_directory_name(B, C),
    directory_file_path(C, exec, D),
    directory_file_path(D, 'prolog_ls.pro', E),
    directory_file_path(D, 'prolog_fmt.pro', F),
    getenv('LIB', G),
    getenv('BIN', H),
    file_directory_name(H, I),
    directory_file_path(I, 'prolog-fmt', J),
    directory_file_path(G, lsp_server, K),
    make_directory_path(K),
    pack_install(lsp_server,
                 [ package_directory(G),
                   global(false),
                   upgrade(true),
                   interactive(false)
                 ]),
    copy_file(E, H),
    copy_file(F, J),
    chmod(H, +x),
    chmod(J, +x),
    halt.
