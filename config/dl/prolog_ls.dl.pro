#!/usr/bin/env -S -- swipl

:- initialization(main, main).

uri("https://raw.githubusercontent.com/adimit/prolog.vim/master/syntax/prolog.vim").

main(_Argv) :-
    current_prolog_flag(os_argv, [_, Arg0|_]),
    getenv('LIB', Lib),
    getenv('BIN', BinD),
    uri(URI),
    file_directory_name(Arg0, Dl),
    file_directory_name(Dl, Config),
    file_directory_name(Config, Root),
    directory_file_path(Root, "syntax", Syntax),
    directory_file_path(Dl, "prolog_ls.ex.pro", BinS),
    directory_file_path(Dl, "prolog_fmt.ex.pro", BinFS),
    directory_file_path(Syntax, "prolog.vim", SynD),
    file_directory_name(BinD, Bin),
    directory_file_path(Bin, 'prolog-fmt.pro', BinFD),
    =(Pack, lsp_server),
    directory_file_path(Lib, Pack, Path),
    make_directory_path(Path),
    pack_install(Pack,
                 [ package_directory(Lib),
                   global(false),
                   upgrade(true),
                   interactive(false)
                 ]),
    setup_call_cleanup(process_create(path("get.sh"),
                                      [URI],
                                      [stdout(pipe(P1))]),
                       read_string(P1, _, SynS),
                       close(P1)),
    copy_file(BinS, BinD),
    copy_file(BinFS, BinFD),
    chmod(BinD, +(x)),
    chmod(BinFD, +(x)),
    copy_file(SynS, SynD).
