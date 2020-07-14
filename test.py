from turing import TuringMachine, R, L, E, Behavior


# ======== Some basic machine definitions


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

# Alternating 1s and 0s with blanks and allowing multiple operations (Petzold p. 84, Turing p. 234)
alternate_compact = {
    'b':
        {E: (['0'], 'b'),
         '0': ([R, R, '1'], 'b'),
         '1': ([R, R, '0'], 'b')}
}

# Binary increment (https://turingmachine.io)
increment = {
    'r':
        {E: ([L], 'c'),
         ('0', '1'): ([R], 'r')},
    'c':
        {E: (['1', L], 'd'),
         '0': (['1', L], 'd'),
         '1': (['0', L], 'c')}
}

# Increasing runs of 1, with alternating blanks (Petzold p. 87, Turing p. 234)
increasing = {
    'b':
        {E: (['ə', R, 'ə', R, '0', R, R, '0', L, L], 'o')},
    'o':
        {'1': ([R, 'x', L, L, L], 'o'),
         '0': ([], 'q')},
    'q':
        {('0', '1'): ([R, R], 'q'),  # REV - Actually "Any"
         E: (['1', L], 'p')},
    'p':
        {'x': ([E, R], 'q'),
         'ə': ([R], 'f'),
         E: ([L, L], 'p')},
    'f':
        {('0', '1'): ([R, R], 'f'),  # REV - Actually "Any"
         E: (['0', L, L], 'o')},
}


# ======== Example machine runs and displays

# -------- Incrementing machine

print("\n======== Incrementing machine")

print("\n-------- Auto halt 500 steps; tape")
increment_machine = TuringMachine('r', increment, initial_tape="101011")
for q in increment_machine.steps(500, auto_halt=True):
    print(q.str_tape())

print("\n-------- All (18) steps; tape")
increment_machine = TuringMachine('r', increment, initial_tape="011111")
for q in increment_machine.steps(18):
    print(q.str_tape())

# TBD - Add support for moving left
# increment_machine = TuringMachine('r', increment, initial_tape="111111")
# for q in increment_machine.steps(500, auto_halt=True):
#     print(q.str_tape())


# -------- Alternating 1/0 machine

print("\n\n======== Alternating 1s and 0s, with blanks")

alternate_machine = TuringMachine('b', alternate, initial_tape=E)

print("\n-------- 10 steps with generator; complete configuration")
for q in alternate_machine.steps(10):
    print(q.str_complete_configuration())

print("\n-------- 10 steps with generator (reset); complete configuration")
for q in alternate_machine.steps(10):
    print(q.str_complete_configuration())

print("........ 10 steps with generator (continue)")
for q in alternate_machine.steps(10, extend=True):
    print(q.str_complete_configuration())

print("........ 3 steps with step/steps(1) (continue)")
alternate_machine.step()
print(alternate_machine.str_complete_configuration())
print(next(alternate_machine.steps(1, extend=True)).str_complete_configuration())
alternate_machine.step()
print(alternate_machine.str_complete_configuration())

print("........ 10 steps with generator (continue)")
for q in alternate_machine.steps(10, extend=True):
    print(q.str_complete_configuration())

# print("----- Endless steps with generator (continue)")
# for q in alternate_machine.steps(auto_halt=True):
#     print(q.str_complete_configuration())

print("\n-------- 10 steps with generator (reset); complete configuration as list")
for q in alternate_machine.steps(10):
    print(q.complete_configuration())

print("\n-------- Above using alternate compact rules")
alternate_machine_compact = TuringMachine('b', alternate_compact, initial_tape=E)
for q in alternate_machine_compact.steps(10):
    print(q.complete_configuration())


# -------- Increasing machine

print("\n\n======== Increasing runs of 1s")

increasing_machine = TuringMachine('b', increasing, initial_tape=E)

print("\n-------- 40 steps with generator; tape")
for q in increasing_machine.steps(40):
    print(q.str_tape())

# TBD - Fix and make more pythonic
print("\n-------- 300 steps with generator; tape filtered")
printed_q = []
for q in increasing_machine.steps(300):
    pq = q.str_tape().rstrip(E)
    if pq not in printed_q:
        if not pq.find("x") >= 0:
            print(pq)
        printed_q = printed_q + [pq]
        #print(printed_q)

print("\n-------- 40 steps with generator; complete config")
for q in increasing_machine.steps(40):
    print(q.str_complete_configuration())

print("\n-------- Turing's compact complete configurations (Petzold p. 92, Turing p. 235)")
increasing_machine.reset()
print(':'.join([x.str_complete_configuration() for x in increasing_machine.steps(8)]))



# Test generator and stepping using simple alternating machine



#
# print("\n ----- Generator (reset)")
# increasing_machine.reset()
# for q in increasing_machine.steps(10):
#     print(q.str_complete_configuration())
#
# print("\n ----- Generator (continue)")
# for q in increasing_machine.steps(10):
#     print(q.str_complete_configuration())
#
# increasing_machine.reset()
# configuration = []
# for q in range(8):
#     configuration.append(increasing_machine.str_complete_configuration())
#     increasing_machine.step()
# print(':'.join(configuration))
#
# print("\n ----- Generator")
# for q in increasing_machine.steps(200, reset=True):
#     print(q.str_tape())
#


# print("\n\nGenerator\n")
# increasing_machine.reset()
# print([x.tape for x in increasing_machine.steps(10)])

# print(transitions['b'][' '])
# print(transitions['f'][' '])
#print(transitions['f'][1])


# transitions = {
#     # this state represents having read an even number of ones
#     0: {
#         '0': (0, '0', R),
#         '1': (1, '1', R),
#         '_': (-1, '_', L),
#         },
#     # this state represents having read an odd number of ones
#     1: {
#         '0': (1, '0', R),
#         '1': (0, '1', R),
#         '_': (-1, '_', R),
#         }
#     }


