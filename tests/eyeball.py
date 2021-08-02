#!/usr/bin/env python
# encoding: utf8

import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from machine import TuringMachine, Table, R, L, N, E, Behavior
from utils import *

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

# Binary increment (https://turingmachine.io)
increment = {
    'r':
        {E: ([L], 'c', "Scanning complete: backup and enter c"),
         ('0', '1'): ([R], 'r', "Scan to the rightmost digit ...")},
    'c':
        {(E, '0'): (['1', L], 'd', "Done: complete carry and enter d"),
         '1': (['0', L], 'c', "Carry ...")}
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

# Blanks to the right, as DN (Petzold p. 177)
blanks_right_dn = 31335317

# 0 to the right, as DN (Petzold p. 177)
zeros_right_dn = 313325317

# 1 to the right, as DN (Petzold p. 177)
ones_right_dn = 3133225317


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

print("\n-------- Auto halt 500 steps; complete configuration, commented")
increment_machine = TuringMachine('r', increment, initial_tape="101011")
for q in increment_machine.steps(500, auto_halt=True):
    print("".join([q.str_complete_configuration().ljust(10), q.step_comment]))

print("\n-------- Auto halt 500 steps; complete configuration, commented, extend tape left")
increment_machine = TuringMachine('r', increment, initial_tape="111111")
for q in increment_machine.steps(15, auto_halt=True):
    print(q.str_tape())

# BUG - Mishandling of blank on left <<<
print("\n-------- BUG BUG BUG Auto halt 500 steps; complete configuration, commented, extend tape left")
increment_machine = TuringMachine('r', increment, initial_tape=" 111111")
for q in increment_machine.steps(15, auto_halt=True):
    print(q.str_tape())


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

# TBD - Fix and make more pythonic <<<
print("\n-------- 1000 steps with generator; tape filtered and trimmed")
printed_q = []
for q in increasing_machine.steps(1000, include_current=False):
    pq = q.str_tape().rstrip(E).lstrip('ə')
    if pq not in printed_q:
        if not pq.find("x") >= 0 and pq[-1] == '0':
            print(pq)
        printed_q = printed_q + [pq]

print("\n-------- 40 steps with generator; complete config")
for q in increasing_machine.steps(40):
    print(q.str_complete_configuration())

print("\n-------- 40 steps with generator; complete config on two lines")
for q in increasing_machine.steps(40):
    print(q.display_text())

# print("\n-------- 1000 steps with generator; complete config on two lines, overwrite")
# print("\n")
# for q in increasing_machine.steps(1000):
#     print_over(q.display_text(), backup=True, delay=0.01)

print("\n-------- Turing's compact complete configurations (Petzold p. 92, Turing p. 235)")
print(':'.join([x.str_complete_configuration() for x in increasing_machine.steps(8)]))


# -------- Machine definition representations; SD, DN, etc.

print("\n\n======== Machine definition representations")

print("\n--------- SD for alternating 1s and 0s, with blanks (Petzold p. 140, Turing p. 241)")

alternate_machine_standard = TuringMachine('b', alternate_standard, initial_tape=E)
print(alternate_machine_standard.instructions('SD'))

print("\n--------- DN for alternating 1s and 0s, with blanks (Petzold p. 140, Turing p. 241)")

alternate_machine_standard = TuringMachine('b', alternate_standard, initial_tape=E)
print(alternate_machine_standard.instructions('DN'))

print("\n--------- Tuple standard form for alternating 1s and 0s, with blanks (Petzold p. 139, Turing p. 241)")

alternate_machine_standard = TuringMachine('b', alternate_standard, initial_tape=E)
print(alternate_machine_standard.instructions('tuples'))

print("\n--------- List of standard form tuples for alternating 1s and 0s, with blanks")

alternate_machine_standard = TuringMachine('b', alternate_standard, initial_tape=E)
print(alternate_machine_standard.instructions('tuples', 'list'))

print("\n--------- Wolfram TuringMachine rules for alternating 1s and 0s, with blanks")

alternate_standard_w_noop = Table(alternate_standard, add_no_op_instructions=True)
alternate_machine_standard = TuringMachine('b', alternate_standard_w_noop, initial_tape=E)
print(alternate_machine_standard.instructions('wolfram'))

print("\n--------- Processing a DN")

dn = 31332531173113353111731113322531111731111335317
sd = "DADDCRDAA;DAADDRDAAA;DAAADDCCRDAAAA;DAAAADDRDA;"
print(Table.dict_from_representation(dn, 'DN'))
print(Table.dict_from_representation(dn, 'DN', m_config_ordering=['P', 'Q', 'r', 'S', 'T']))
print(Table.dict_from_representation(dn, 'DN', m_config_ordering=['W', 'X', 'Y', 'Z']))
print(TuringMachine('b', Table.dict_from_representation(dn, 'DN')).instructions('DN'))
print(TuringMachine('b', Table.dict_from_representation(dn, 'DN')).instructions('tuples'))
print(TuringMachine('b', Table.dict_from_representation(dn, 'DN')).instructions('SD'))
print(TuringMachine('b', Table(Table.dict_from_representation(dn, 'DN'),
                               add_no_op_instructions=True)).instructions('wolfram'))
print(Table.dict_from_representation(sd, 'SD'))
print(Table.dict_from_representation(sd, 'SD', m_config_ordering=['P', 'Q', 'r', 'S', 'T']))
print(Table.dict_from_representation(sd, 'SD', m_config_ordering=['W', 'X', 'Y', 'Z']))
print(TuringMachine('b', Table.dict_from_representation(sd, 'SD')).instructions('DN'))
print(TuringMachine('b', Table.dict_from_representation(sd, 'SD')).instructions('tuples'))
print(TuringMachine('b', Table.dict_from_representation(sd, 'SD')).instructions('SD'))
print(TuringMachine('b', Table(Table.dict_from_representation(sd, 'SD'),
                               add_no_op_instructions=True)).instructions('wolfram'))

print("\n--------- YAML for alternating 1s and 0s, with blanks (for https://turingmachine.io)")

alternate_machine_standard = TuringMachine('b', alternate_standard, initial_tape=E)
print(alternate_machine_standard.instructions('YAML'))

print("\n--------- Dictionary for alternating 1s and 0s, with blanks")

alternate_machine_standard = TuringMachine('b', alternate_standard, initial_tape=E)
print(alternate_machine_standard.instructions())

print("\n--------- The first 8 steps for the left to right machines with the three lowest DNs (Petzold, p. 177)")
for dn in [blanks_right_dn, zeros_right_dn, ones_right_dn]:
    for q in TuringMachine('q1', Table.dict_from_representation(dn, 'DN')).steps(8):
        print(q.str_tape())



# -------- Orderings of m-configurations and symbols

print("\n\n======== Orderings of m-configurations and symbols")

increasing_machine = TuringMachine('b', increasing, initial_tape=E)
print("\n-------- Default symbol ordering, increasing number of 1s")
print(increasing_machine._table._m_config_ordering)
print(increasing_machine._table._symbol_ordering)

increasing_reordered = Table(increasing, m_config_ordering=['f', 'p', 'b', 'q', 'o'], e_symbol_ordering=['ə', 'x'])
increasing_machine = TuringMachine('b', increasing_reordered, initial_tape=E)
print("\n-------- Customized symbol ordering, increasing number of 1s")
print(increasing_machine._table._m_config_ordering)
print(increasing_machine._table._symbol_ordering)

alternate_machine_standard = TuringMachine('b', alternate_standard, initial_tape=E)
print("\n-------- Default symbol ordering, alternating 0s and 1s")
print(alternate_machine_standard._table._m_config_ordering)
print(alternate_machine_standard._table._symbol_ordering)
print(alternate_machine_standard.instructions('tuples'))

alternate_standard_reordered = Table(alternate_standard, m_config_ordering=['f', 'c', 'e', 'b'])
alternate_machine_standard = TuringMachine('b', alternate_standard_reordered, initial_tape=E)
print("\n-------- Customized symbol ordering, alternating 0s and 1s")
print(alternate_machine_standard._table._m_config_ordering)
print(alternate_machine_standard._table._symbol_ordering)
print(alternate_machine_standard.instructions('tuples'))



# -------- Debug

print("\n\n======== DEBUG")

# print("\n-------- Test bad m-configuration")
# alternate_machine_compact = TuringMachine('Z', alternate_compact, initial_tape=E)
# for q in alternate_machine_compact.steps(10, debug = True):
#     print(q.complete_configuration())

# print("\n-------- Test bad symbol")
# alternate_machine_compact = TuringMachine('b', alternate_compact, initial_tape="X")
# for q in alternate_machine_compact.steps(10, debug = True):
#     print(q.complete_configuration())

# print("\n-------- Test attempt to use non-standard configuration where reqired")
# alternate_machine_compact = TuringMachine('b', alternate_compact, initial_tape="X")
# print(alternate_machine_compact.instructions())
# print(alternate_machine_compact.instructions('SD'))
