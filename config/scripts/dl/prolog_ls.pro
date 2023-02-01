#!/usr/bin/env -S -- swipl

:- initialization(main).

main(_Argv) :-
    current_prolog_flag(os_argv, [_, Arg0|_]),
    file_directory_name(Arg0, Parent),
    file_directory_name(Parent, GrandParent),
    directory_file_path(GrandParent, 'exec', Exec),
    directory_file_path(Exec, 'prolog_ls.pro', BinS),
    directory_file_path(Exec, 'prolog_fmt.pro', BinFS),
    getenv('LIB', Lib),
    getenv('BIN', BinD),
    file_directory_name(BinD, Bin),
    directory_file_path(Bin, 'prolog-fmt', BinFD),
    directory_file_path(Lib, 'lsp_server', Path),

    make_directory_path(Path),
    pack_install(lsp_server,
                 [ package_directory(Lib),
                   global(false),
                   upgrade(true),
                   interactive(false)
                 ]),
    copy_file(BinS, BinD),
    copy_file(BinFS, BinFD),
    chmod(BinD, +x),
    chmod(BinFD, +x),

    halt.
