#!/usr/bin/env -S -- swipl

:- initialization(main, main).

shebang(Stream, [Line]) :-
    =(Bang, "#!"),
    string_length(Bang, Len),
    peek_string(Stream, Len, Bang),
    read_line_to_string(Stream, Line).

shebang(_, []).

pprint_comments([]).

pprint_comments([-(_, Comment)|Comments]) :-
    writeln(Comment),
    pprint_comments(Comments).

pprint(Stream, _) :-
    at_end_of_stream(Stream).

pprint(Stream, _) :-
    =(NL, '\n'),
    peek_char(Stream, NL),
    get_char(Stream, NL),
    pprint(Stream, [NL]).

pprint(Stream, Print) :-
    read_term(Stream,
              Term,
              [variable_names(Names), comments(Comments)]),
    maplist(write, Print),
    pprint_comments(Comments),
    portray_clause(user_output,
                   Term,
                   [ variable_names(Names),
                     quoted(true),
                     ignore_ops(true)
                   ]),
    pprint(Stream, []).

main(_Argv) :-
    shebang(user_input, Line),
    maplist(writeln, Line),
    pprint(user_input, []).
