#!/usr/bin/env -S -- swipl

:- initialization(main, main).

:- use_module(library(/(dcg, basics))).

x_uuid(UUID) :-
    uuid(ID),
    split_string(ID, "-", "", Parts),
    atomics_to_string(["X"|Parts], "", UUID).

uuid_gen(String, Placeholder) :-
    x_uuid(Prefix),
    string_length(Prefix, PLen),
    string_length(String, SLen),
    is(Padding, max(0, -(-(SLen, PLen), 2))),
    length(PS, Padding),
    maplist(=("_"), PS),
    atomics_to_string([Prefix|PS], "", Holder),
    atom_string(Placeholder, Holder).

p_other([str(String, Placeholder)|XS]) -->
    `0'\\\\`,
    { string_codes(String, `0'\\\\`),
      uuid_gen(String, Placeholder)
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
      uuid_gen(String, Placeholder)
    },
    p_other(XS).

p_other([norm(X)|XS]) -->
    [X],
    { maplist(dif(X), `\`'"`)
    },
    p_other(XS).

p_other([]) -->
    [].

p_others_inner([str(String, Placeholder)|Tokens], Codes, [no(Str), str(String, Placeholder)|Syntax]) :-
    string_codes(Str, Codes),
    p_others_inner(Tokens, [], Syntax).

p_others_inner([norm(C)|Tokens], CS, Syntax) :-
    append(CS, [C], Codes),
    p_others_inner(Tokens, Codes, Syntax).

p_others_inner([], Codes, [no(String)]) :-
    string_codes(String, Codes).

p_others(Syntax) -->
    p_other(Tokens),
    { p_others_inner(Tokens, [], Syntax)
    }.

p_others([]) -->
    [].

p_string_inner(Mark, [0'\\, 0'\\|X]) -->
    `\\\\`,
    p_string_inner(Mark, X).

p_string_inner(Mark, [0'\\, Mark|X]) -->
    [0'\\, Mark],
    p_string_inner(Mark, X).

p_string_inner(Mark, [X|XS]) -->
    { dif(X, Mark)
    },
    [X],
    p_string_inner(Mark, XS).

p_string_inner(_, []) -->
    [].

p_codes(Mark, str(String, Placeholder)) -->
    [Mark],
    p_string_inner(Mark, XS),
    [Mark],
    { append([Mark|XS], [Mark], Codes),
      string_codes(String, Codes),
      uuid_gen(String, Placeholder)
    }.

p_string(Mark, no(String)) -->
    [Mark],
    p_string_inner(Mark, XS),
    [Mark],
    { append([Mark|XS], [Mark], Codes),
      string_codes(String, Codes)
    }.

p_strings([String]) -->
    (   p_codes(0'`, String)
    ;   p_string(0'', String)
    ;   p_string(0'", String)
    ).

p_strings([]) -->
    [].

p_grammar([]) -->
    [].

p_grammar(Syntax) -->
    p_others(Ignored),
    p_strings(String1),
    p_grammar(String2),
    { append(String1, String2, Strings),
      append(Ignored, Strings, Syntax)
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

pprint_comments(Stream, [-(_, Comment)|Comments]) :-
    writeln(Stream, Comment),
    pprint_comments(Stream, Comments).

pprint(StreamIn, _) :-
    at_end_of_stream(StreamIn).

pprint(StreamIn, StreamOut) :-
    read_term(StreamIn,
              Term,
              [variable_names(Names), comments(Comments)]),
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
                         seek(StreamOut, 0, bof, _)
                       ),
                       close(StreamOut)),
    read_file_to_string(Tmp, Prettied, []),
    unparse_text(Prettied, Mapping, Output),
    write(Output).
