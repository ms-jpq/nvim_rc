#!/usr/bin/env -S -- swipl
:- (initialization main).
read_lines(A, []) :-
    at_end_of_stream(A).
read_lines(A, [B|C]) :-
    read_line_to_string(A, B),
    read_lines(A, C).
shebang(A) :-
    B="#!",
    string_length(B, C),
    sub_string(A, 0, C, _, "#!"),
    write(A),
    nl.
fmt_terms(A) :-
    at_end_of_stream(A).
fmt_terms(A) :-
    read_term(A, B, []),
    portray_clause(B),
    fmt_terms(A).
main(_) :-
    current_prolog_flag(os_argv, [_, A|_]),
    file_directory_name(A, B),
    chdir(B),
    read_lines(user_input, C),
    exclude(shebang, C, D),
    atomic_list_concat(D, "\n", E),
    open_string(E, F),
    fmt_terms(F),
    halt.
