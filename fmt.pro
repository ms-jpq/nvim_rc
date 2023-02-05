#!/usr/bin/env -S -- swipl

:- initialization(main, main).

:- use_module(library(/(dcg, basics))).

uuid_gen(String, Placeholder) :-
    =(Underscore, "_"),
    string_length(String, SLen),
    uuid(UUID),
    split_string(UUID, "-", "", Parts),
    atomics_to_string(["X"|Parts],
                      Underscore,
                      Prefix),
    string_length(Prefix, PLen),
    is(Padding, max(0, -(-(SLen, PLen), 2))),
    length(PS, Padding),
    maplist(=(Underscore), PS),
    atomics_to_string([Prefix|PS], "", Holder),
    atom_string(Placeholder, Holder).

p_other([48, 39, X|XS]) -->
    [48, 39, X],
    { dif(X, 39)
    },
    p_other(XS).

p_other([X|XS]) -->
    [X],
    { maplist(dif(X), [96, 39, 34])
    },
    p_other(XS).

p_other([]) -->
    [].

p_others([no(String)]) -->
    p_other(Codes),
    { string_codes(String, Codes)
    }.

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

p_strings(String) -->
    p_string(96, String).

p_strings(String) -->
    p_string(39, String).

p_strings(String) -->
    p_string(34, String).

p_grammar(Syntax) -->
    p_others(Ignored),
    p_strings(String1),
    p_grammar(String2),
    { append(Ignored,
             [String1|String2],
             Syntax)
    }.

p_grammar(Syntax) -->
    p_others(Syntax).

p_grammar([]) -->
    [].

read_array(Input, Parsed, Unparsed) :-
    string_codes(Input, Codes),
    phrase(p_grammar(Parsed), Codes, Rest),
    string_codes(Unparsed, Rest).

build_mapping([no(String)|StrIn], [String|StrOut], Mapping) :-
    build_mapping(StrIn, StrOut, Mapping).

build_mapping([str(String, Placeholder)|StrIn], [Slot|StrOut], [=(Placeholder, String)|Mapping]) :-
    atomics_to_string(["{", Placeholder, "}"], "", Slot),
    build_mapping(StrIn, StrOut, Mapping).

build_mapping([], [], []).

parse_text(TextIn) :-
    read_array(TextIn, Parsed, ""),
    build_mapping(Parsed, IR, Mapping),
    atomics_to_string(IR, "", TextOut),
    interpolate_string(TextOut,
                       Interpolated,
                       Mapping,
                       []),
    =(Interpolated, TextIn),
    writeln("----------------------------------------------------------------------------"),
    writeln(TextIn),
    writeln(Interpolated),
    writeln(Mapping).

main() :-
    read_file_to_string("./test.txt", Txt, []),
    string_lines(Txt, Lines),
    maplist(parse_text, Lines).

end_of_file.
