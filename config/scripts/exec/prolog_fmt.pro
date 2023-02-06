#!/usr/bin/env -S -- swipl

:- initialization(main, main).

:- set_portray_text(enabled, true).

:- set_portray_text(min_length, 1).

shebang(Stream, [Line]) :-
    =(Bang, "#!"),
    string_length(Bang, Len),
    peek_string(Stream, Len, Bang),
    read_line_to_string(Stream, Line).

shebang(_, []).

pprint_comments(_, []).

pprint_comments(Stream, [-(_, Comment)|Comments]) :-
    writeln(Stream, Comment),
    pprint_comments(Stream, Comments).

pprint(StreamIn, _) :-
    at_end_of_stream(StreamIn).

pprint(StreamIn, StreamOut) :-
    read_term(StreamIn,
              Term,
              [variable_names(Names), comments(Comments)]),
    nl,
    pprint_comments(StreamOut, Comments),
    portray_clause(StreamOut,
                   Term,
                   [ variable_names(Names),
                     ignore_ops(true),
                     quoted(true)
                   ]),
    pprint(StreamIn, StreamOut).

main(_Argv) :-
    =(StreamIn, user_input),
    setup_call_cleanup(tmp_file_stream(text, Tmp, StreamOut),
                       ( shebang(StreamIn, Line),
                         maplist(writeln(StreamOut), Line),
                         pprint(StreamIn, StreamOut),
                         seek(StreamOut, 0, bof, _)
                       ),
                       close(StreamOut)),
    read_file_to_string(Tmp, Output, []),
    write(Output).
