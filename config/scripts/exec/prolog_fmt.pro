#!/usr/bin/env -S -- swipl

:- initialization(main).

shebang(Stream, [Line]) :-
    Bang = "#!",
    string_length(Bang, Len),
    peek_string(Stream, Len, Bang),
    read_line_to_string(Stream, Line).

shebang(_, []).


fmt_terms(Stream) :-
    at_end_of_stream(Stream).

fmt_terms(Stream) :-
    read_term(Stream, Term, []),
    portray_clause(Term),
    fmt_terms(Stream).


main(_Argv) :-
    current_prolog_flag(os_argv, [_, Arg0|_]),
    file_directory_name(Arg0, Dir),
    chdir(Dir),

    shebang(user_input, Line),
    maplist(writeln, Line),
    fmt_terms(user_input),

    halt.
