#!/usr/bin/env -S -- swipl

:- initialization(main, main).

x_uuid(UUID) :-
    uuid(ID),
    split_string(ID, "-", "", Parts),
    atomics_to_string(["X"|Parts], "", UUID).

uuid_padded(String, Placeholder) :-
    x_uuid(Prefix),
    string_length(Prefix, PLen),
    string_length(String, SLen),
    is(Padding, max(0, -(-(SLen, PLen), 2))),
    length(PS, Padding),
    maplist(=("_"), PS),
    atomics_to_string([Prefix|PS], "", Holder),
    atom_string(Placeholder, Holder).

p_other([str("0'\\\\", Placeholder)|XS]) -->
    `0'\\\\`,
    { uuid_padded("", Placeholder)
    },
    p_other(XS).

p_other([str(String, Placeholder)|XS]) -->
    [ 0'0,
      0'',
      X
    ],
    { string_codes(String,
                   [ 0'0,
                     0'',
                     X
                   ]),
      uuid_padded(String, Placeholder)
    },
    p_other(XS).

p_other([norm(X)|XS]) -->
    [X],
    { maplist(dif(X), `\`'"`)
    },
    p_other(XS).

p_other([]) -->
    [].

p_others_inner([norm(C)|Tokens], CS, Syntax) :-
    append(CS, [C], Codes),
    p_others_inner(Tokens, Codes, Syntax).

p_others_inner([str(String, Placeholder)|Tokens], Codes, [no(Str), str(String, Placeholder)|Syntax]) :-
    string_codes(Str, Codes),
    p_others_inner(Tokens, [], Syntax).

p_others_inner([], Codes, [no(String)]) :-
    string_codes(String, Codes).

p_others(Syntax) -->
    p_other(Tokens),
    { p_others_inner(Tokens, [], Syntax)
    }.

p_string_inner(Mark, [0'\\, X|XS]) -->
    [0'\\, X],
    { memberchk(X,
                [0'\\, Mark])
    },
    p_string_inner(Mark, XS).

p_string_inner(Mark, [X|XS]) -->
    [X],
    { dif(X, Mark)
    },
    p_string_inner(Mark, XS).

p_string_inner(_, []) -->
    [].

p_str(Mark, XS) -->
    [Mark],
    p_string_inner(Mark, XS),
    [Mark].

p_string(Mark, no(String)) -->
    p_str(Mark, XS),
    { append([Mark|XS], [Mark], Codes),
      string_codes(String, Codes)
    }.

p_codes(Mark, str(String, Placeholder)) -->
    p_str(Mark, XS),
    { append([Mark|XS], [Mark], Codes),
      string_codes(String, Codes),
      uuid_padded(String, Placeholder)
    }.

p_strings([String]) -->
    (   p_string(0'', String)
    ;   p_string(0'", String)
    ;   p_codes(0'`, String)
    ).

p_strings([]) -->
    [].

p_grammar([]) -->
    [].

p_grammar(Syntax) -->
    p_others(S1),
    p_strings(S2),
    p_grammar(S3),
    { append(S1, S2, S),
      append(S, S3, Syntax)
    }.

build_mapping([no(String)|StrIn], [String|StrOut], Mapping) :-
    build_mapping(StrIn, StrOut, Mapping).

build_mapping([str(String, Placeholder)|StrIn], [Slot|StrOut], [=(Placeholder, String)|Mapping]) :-
    atomics_to_string(['"{', Placeholder, '}"'], "", Slot),
    build_mapping(StrIn, StrOut, Mapping).

build_mapping([], [], []).

parse_text(StreamIn, Mapping, TextOut) :-
    phrase_from_stream(p_grammar(Parsed), StreamIn),
    build_mapping(Parsed, IR, Mapping),
    atomics_to_string(IR, "", TextOut).

unparse_text(TextIn, Mapping, TextOut) :-
    re_replace(/('"(\\{X[0-9a-f]{32}_*\\})"', g),
               "$1",
               TextIn,
               IR),
    interpolate_string(IR, TextOut, Mapping, []).

shebang(Stream, [Line]) :-
    =(Bang, "#!"),
    string_length(Bang, Len),
    peek_string(Stream, Len, Bang),
    read_line_to_string(Stream, Line).

shebang(_, []).

pprint_comments(_, []).

pprint_comments(Stream, [-(Position, Comment)|Comments]) :-
    stream_position_data(line_count, Position, _Row),
    stream_position_data(line_position, Position, _Col),
    writeln(Stream, Comment),
    pprint_comments(Stream, Comments).

pprint(StreamIn, _) :-
    at_end_of_stream(StreamIn).

pprint(StreamIn, StreamOut) :-
    read_term(StreamIn,
              Term,
              [ variable_names(Names),
                term_position(_Position),
                comments(Comments)
              ]),
    nl(StreamOut),
    pprint_comments(StreamOut, Comments),
    portray_clause(StreamOut,
                   Term,
                   [ variable_names(Names),
                     ignore_ops(true),
                     quoted(true)
                   ]),
    pprint(StreamIn, StreamOut).

main(_Argv) :-
    parse_text(user_input, Mapping, Preprocessed),
    open_string(Preprocessed, StreamIn),
    setup_call_cleanup(tmp_file_stream(text, Tmp, StreamOut),
                       ( shebang(StreamIn, Line),
                         maplist(writeln(StreamOut), Line),
                         pprint(StreamIn, StreamOut),
                         flush_output(StreamOut)
                       ),
                       close(StreamOut)),
    read_file_to_string(Tmp, Prettied, []),
    unparse_text(Prettied, Mapping, Output),
    writeln(user_error, "---"),
    write(user_output, Output),
    writeln(user_error, "---").
