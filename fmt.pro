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

p_not(CS, [X|XS]) -->
    [X],
    { maplist(dif(X), CS)
    },
    p_not(CS, XS).

p_not(_, []) -->
    [].

p_nots(CodePoints, no(String)) -->
    p_not(CodePoints, Codes),
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

p_grammar([Ignored, String1|String2]) -->
    p_nots([96, 39, 34], Ignored),
    p_strings(String1),
    p_grammar(String2).

p_grammar([Ignored]) -->
    p_nots([96, 39, 34], Ignored).

p_grammar([]) -->
    [].

read_array(Input, Parsed, Unparsed) :-
    string_codes(Input, Codes),
    phrase(p_grammar(Parsed), Codes, Rest),
    string_codes(Unparsed, Rest).

build_mapping([no(String)|StrIn], [String|StrOut], Map) :-
    build_mapping(StrIn, StrOut, Map).

build_mapping([str(String, Placeholder)|StrIn], [Slot|StrOut], [=(Placeholder, String)|Map]) :-
    atomics_to_string(["{", Placeholder, "}"], "", Slot),
    build_mapping(StrIn, StrOut, Map).

build_mapping([], [], []).

parse_text(TextIn) :-
    read_array(TextIn, Parsed, ""),
    build_mapping(Parsed, IR, Map),
    atomics_to_string(IR, "", TextOut),
    interpolate_string(TextOut,
                       Interpolated,
                       Map,
                       []),
    =(Interpolated, TextIn),
    writeln("----------------------------------------------------------------------------"),
    writeln(TextIn),
    writeln(Interpolated),
    writeln(Map).

main() :-
    read_file_to_string("./test.txt", Txt, []),
    string_lines(Txt, Lines),
    maplist(parse_text, Lines).

end_of_file.
