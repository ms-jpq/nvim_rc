#!/usr/bin/env -S -- swipl

:- initialization(main).

shebang(Stream, [Line]) :-
    =(Bang, "#!"),
    string_length(Bang, Len),
    peek_string(Stream, Len, Bang),
    read_line_to_string(Stream, Line).

shebang(_, []).

fmt_comments([]).

fmt_comments([-(_, Comment)|Comments]) :-
    writeln(Comment),
    fmt_comments(Comments).

fmt_terms(Stream, _) :-
    at_end_of_stream(Stream).

fmt_terms(Stream, _) :-
    =(NL, '\n'),
    peek_char(Stream, NL),
    get_char(Stream, NL),
    fmt_terms(Stream, [NL]).

fmt_terms(Stream, Print) :-
    read_term(Stream,
              Term,
              [variable_names(Names), comments(Comments)]),
    maplist(write, Print),
    fmt_comments(Comments),
    portray_clause(user_output,
                   Term,
                   [ variable_names(Names),
                     quoted(true),
                     ignore_ops(true)
                   ]),
    fmt_terms(Stream, []).

main(_Argv) :-
    shebang(user_input, Line),
    maplist(writeln, Line),
    fmt_terms(user_input, []),
    halt.
