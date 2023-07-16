#!/usr/bin/env -S -- swipl

:- initialization(main, main).

main(_Argv) :-
    current_prolog_flag(os_argv, [_, Arg0|_]),
    getenv('LIB', Lib),
    getenv('BIN', BinD),
    getenv('URI', URI),
    file_directory_name(Arg0, Dl),
    file_directory_name(Dl, Scripts),
    file_directory_name(Scripts, Config),
    file_directory_name(Config, Root),
    directory_file_path(Scripts, "exec", Exec),
    directory_file_path(Root, "syntax", Syntax),
    directory_file_path(Exec, "prolog_ls.pro", BinS),
    directory_file_path(Exec, "prolog_fmt.pro", BinFS),
    directory_file_path(Syntax, "prolog.vim", SynD),
    file_directory_name(BinD, Bin),
    directory_file_path(Bin, 'prolog-fmt', BinFD),
    =(Pack, lsp_server),
    directory_file_path(Lib, Pack, Path),
    make_directory_path(Path),
    pack_install(Pack,
                 [ package_directory(Lib),
                   global(false),
                   upgrade(true),
                   interactive(false)
                 ]),
    setup_call_cleanup(process_create(path("get"),
                                      ["--", URI],
                                      [stdout(pipe(P1))]),
                       read_string(P1, _, SynS),
                       close(P1)),
    copy_file(BinS, BinD),
    copy_file(BinFS, BinFD),
    chmod(BinD, +(x)),
    chmod(BinFD, +(x)),
    copy_file(SynS, SynD).
