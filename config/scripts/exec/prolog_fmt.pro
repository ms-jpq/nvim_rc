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

p_comment_line_inner(Line, Parsed) :-
    sub_string(Line, 0, 1, _, "*"),
    string_concat(" ", Line, Parsed).

p_comment_line_inner(Line, Line).

p_comment_line(Line, Parsed) :-
    normalize_space(string(NoSpaces), Line),
    p_comment_line_inner(NoSpaces, Parsed).

p_comments([], []).

p_comments([-(Position, Comment)|Comments], [-([Row, 0], Lines, comment)|LS]) :-
    stream_position_data(line_count, Position, Row),
    string_lines(Comment, CommentLines),
    maplist(p_comment_line, CommentLines, Lines),
    p_comments(Comments, LS).

p_terms_inner(Row, [Line|Lines], [-([Row, 1], Line, term(Indent))|LS]) :-
    normalize_space(string(NoSpaces), Line),
    string_length(NoSpaces, Indent),
    is(R, +(Row, 1)),
    p_terms_inner(R, Lines, LS).

p_terms_inner(_, [], []).

p_term(Term, Names, Row, Parsed) :-
    with_output_to(string(String),
                   ( current_output(Stream),
                     portray_clause(Stream,
                                    Term,
                                    [ variable_names(Names),
                                      ignore_ops(true),
                                      quoted(true)
                                    ])
                   )),
    string_lines(String, Lines),
    p_terms_inner(Row, Lines, Parsed).

pprint_rows(Indent, [-(_, Lines, comment)|LS], Adjusted) :-
    reverse(Lines, RL),
    append(RL, AS, Adjusted),
    pprint_rows(Indent, LS, AS).

pprint_rows(_, [-(_, Line, term(Indent))|LS], [Line|AS]) :-
    pprint_rows(Indent, LS, AS).

pprint_rows(_, [], []).

pprint(StreamIn, _) :-
    at_end_of_stream(StreamIn).

pprint(StreamIn, StreamOut) :-
    read_term(StreamIn,
              Term,
              [ variable_names(Names),
                term_position(Position),
                comments(Comments)
              ]),
    stream_position_data(line_count, Position, Row),
    p_term(Term, Names, Row, ParsedTerm),
    p_comments(Comments, ParsedComments),
    append(ParsedTerm, ParsedComments, Rows),
    sort(1, @>=, Rows, Sorted),
    nl(StreamOut),
    pprint_rows(0, Sorted, Adjusted),
    reverse(Adjusted, Lines),
    maplist(writeln(StreamOut), Lines),
    pprint(StreamIn, StreamOut).

main(_Argv) :-
    parse_text(user_input, Mapping, Preprocessed),
    open_string(Preprocessed, StreamIn),
    shebang(StreamIn, Line),
    with_output_to(string(Prettied),
                   ( current_output(StreamOut),
                     maplist(writeln(StreamOut), Line),
                     pprint(StreamIn, StreamOut)
                   )),
    unparse_text(Prettied, Mapping, Output),
    write(user_output, Output).
