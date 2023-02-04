#!/usr/bin/env -S -- swipl

:- initialization(main, main).

:- use_module(library(/(dcg, basics))).

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

p_string(Mark, str(String)) -->
    [Mark],
    p_string_inner(Mark, XS),
    [Mark],
    { string_codes(String, XS)
    }.

p_grammar([Ignored, String1|String2]) -->
    p_nots([96, 39, 34], Ignored),
    p_string(34, String1),
    p_grammar(String2).

p_grammar([Ignored]) -->
    p_nots([96, 39, 34], Ignored).

p_grammar([]) -->
    [].

read_array(Input, Parsed, Unparsed) :-
    string_codes(Input, Codes),
    phrase(p_grammar(Parsed), Codes, Rest),
    string_codes(Unparsed, Rest).

parse_line(Line) :-
    read_array(Line, Parsed, ""),
    writeln(Parsed).

main() :-
    read_file_to_string("./test.txt", Txt, []),
    string_lines(Txt, Lines),
    maplist(parse_line, Lines).

end_of_file.
