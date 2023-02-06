#!/usr/bin/env -S -- swipl

:- initialization(main, main).

:- use_module(library(/(dcg, basics))).

x_uuid(UUID) :-
    uuid(ID),
    split_string(ID, "-", "", Parts),
    atomics_to_string(["X"|Parts], "", UUID).

uuid_gen(String, Placeholder) :-
    string_length(String, SLen),
    x_uuid(Prefix),
    string_length(Prefix, PLen),
    is(Padding, max(0, -(-(SLen, PLen), 2))),
    length(PS, Padding),
    maplist(=("_"), PS),
    atomics_to_string([Prefix|PS], "", Holder),
    atom_string(Placeholder, Holder).

p_other([str(String, Placeholder)|XS]) -->
    [48, 39, X],
    { dif(X, 39),
      string_codes(String, [48, 39, X]),
      uuid_gen(String, Placeholder)
    },
    p_other(XS).

p_other([norm(X)|XS]) -->
    [X],
    { maplist(dif(X), [96, 39, 34])
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

p_string_inner(Mark, [92, Mark|X]) -->
    [92, Mark],
    p_string_inner(Mark, X).

p_string_inner(Mark, [X|XS]) -->
    { dif(X, Mark)
    },
    [X],
    p_string_inner(Mark, XS).

p_string_inner(_, []) -->
    [].

p_string(Mark, str(String, Placeholder)) -->
    [Mark],
    p_string_inner(Mark, XS),
    [Mark],
    { append([Mark|XS], [Mark], Codes),
      string_codes(String, Codes),
      uuid_gen(String, Placeholder)
    }.

p_strings([String]) -->
    (   p_string(96, String)
    ;   p_string(39, String)
    ;   p_string(34, String)
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

read_array(Input, Parsed, Unparsed) :-
    string_codes(Input, Codes),
    phrase(p_grammar(Parsed), Codes, Rest),
    string_codes(Unparsed, Rest).

build_mapping([no(String)|StrIn], [String|StrOut], Mapping) :-
    build_mapping(StrIn, StrOut, Mapping).

build_mapping([str(String, Placeholder)|StrIn], [Slot|StrOut], [=(Placeholder, String)|Mapping]) :-
    atomics_to_string(['"{', Placeholder, '}"'], "", Slot),
    build_mapping(StrIn, StrOut, Mapping).

build_mapping([], [], []).

parse_text(TextIn, Mapping, TextOut) :-
    read_array(TextIn, Parsed, ""),
    build_mapping(Parsed, IR, Mapping),
    atomics_to_string(IR, "", TextOut).

unparse_text(TextIn, Mapping, TextOut) :-
    re_replace(/('"(\\{X[0-9a-f]{32}_*\\})"', g),
               "$1",
               TextIn,
               IR),
    interpolate_string(IR, TextOut, Mapping, []).

parse_many(Text1) :-
    parse_text(Text1, Mapping, Text2),
    unparse_text(Text2, Mapping, Text3),
    writeln("----------------------------------------------------------------------------"),
    writeln(Text1),
    writeln(Text3).

main() :-
    read_file_to_string("./test.txt", Txt, []),
    string_lines(Txt, Lines),
    maplist(parse_many, Lines).

end_of_file.
