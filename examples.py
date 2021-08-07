

# Alternating 1s and 0s with blanks (Petzold p. 81, Turing p. 233))
alternate = {
    'b':
        {E: (['0', R], 'c')},
    'c':
        {E: Behavior([R], 'e')},
    'e':
        {E: (['1', R], 'f')},
    'f':
        {E: ([R], 'b')}
}
alternate_machine = TuringMachine('b', alternate)

# Alternating 1s and 0s with blanks and allowing multiple operations (Petzold p. 84, Turing p. 234)
alternate_compact = {
    'b':
        {E: (['0'], 'b'),
         '0': ([R, R, '1'], 'b'),
         '1': ([R, R, '0'], 'b')}
}
alternate_compact_machine = TuringMachine('b', alternate_compact)

# Alternating 1s and 0s with blanks, in standard form (Petzold p. 139, Turing p. 241))
alternate_standard = {
    'b':
        {E: (['0', R], 'c')},
    'c':
        {E: ([E, R], 'e')},
    'e':
        {E: (['1', R], 'f')},
    'f':
        {E: ([E, R], 'b')}
}
alternate_standard_machine = TuringMachine('b', alternate_standard)

# Binary increment (https://turingmachine.io)
increment = {
    'r':
        {E: ([L], 'c', "Scanning complete: backup and enter c"),
         ('0', '1'): ([R], 'r', "Scan to the rightmost digit...")},
    'c':
        {(E, '0'): (['1', L], 'd', "Done: complete carry and enter d"),
         '1': (['0', L], 'c', "Carry...")}
}
increment_machine = TuringMachine('r', increment, initial_tape='1011101111111')

increasing = {
    'b':
        {E: (['ə', R, 'ə', R, '0', R, R, '0', L, L], 'o', "Initialize")},
    'o':
        {'1': ([R, 'x', L, L, L], 'o', "Mark a block of consecutive 1s..."),
         '0': ([], 'q', "Done marking 1s")},
    'q':
        {('0', '1'): ([R, R], 'q', "Scan right along written F squares..."),
         E: (['1', L], 'p', "Write a 1 and move to the preceding E square")},
    'p':
        {'x': ([E, R], 'q'),
         'ə': ([R], 'f'),
         E: ([L, L], 'p')},
    'f':
        {('0', '1'): ([R, R], 'f', "Scan right along written F squares..."),
         E: (['0', L, L], 'o', "Write a 0 and move to the preceding F square")},
}
increasing_machine = TuringMachine('b', increasing, initial_tape=E)

