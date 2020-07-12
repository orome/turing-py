#!/usr/bin/env python
# encoding: utf8

""" 
A simple Turing Machine implementation aimed at simulating the machines in Turing's 1936 paper.

.. note::
    Any additional note.
"""

#import os

L = -1
R = +1
N = 0
blank = ' '

# TBD - Support for versions on p. 84 and 87 of Petzold <<<
class TuringMachine(object):

    def __init__(self, initial_m_configuration: str, transitions: dict, initial_tape: list = [' '], #halt_state=100,
                 *args, **kw):
        self._initial_tape = initial_tape
        self._initial_m_configuration = initial_m_configuration
        self.transitions = transitions
        #self._halt_state = halt_state
        # Set initial configuration
        # TBD - Add ability to set other than defaults with optional arguments
        self._initial_position = 0

        self.tape = self._initial_tape
        self.m_configuration = self._initial_m_configuration
        self.position = self._initial_position

        self.reset()

    def reset(self) -> None:
        self.tape = self._initial_tape
        self.m_configuration = self._initial_m_configuration
        self.position = self._initial_position

    # TBD - Trim unnecessary
    def get_tape(self) -> list:
        padded_tape = self.tape.copy()
        if self.position > len(self.tape) - 1:
            while self.position > len(padded_tape) - 1:
                padded_tape.append(blank)
        return padded_tape
        # TBD - Grow left!!
    
    def list_complete_configuration(self) -> list:
        scratch_tape = self.get_tape()
        scratch_tape.insert(self.position, self.m_configuration)
        return scratch_tape

    def str_complete_configuration(self) -> str:
        list_complted_config_as_strings =[str(elem) for elem in self.list_complete_configuration()]
        # TBD: check these are all of lenght 1 or there is padding / delimiter provided
        return ''.join(list_complted_config_as_strings)

    # TBD: Fix tape extention and associated copying; add both directions <<<
    def step(self) -> None:
        padded_tape = self.get_tape()
        # print('foo: ' + padded_tape[self.position])
        rule = transitions[self.m_configuration][padded_tape[self.position]]
        if rule[0] is not None:
            padded_tape[self.position] = rule[0]
        self.tape = padded_tape.copy()
        self.position += rule[1]
        self.m_configuration = rule[2]
        #self.position += 1


transitions = {'b':
                   {blank: (0, R, 'c')},
               'c':
                   {blank: (None, R, 'e')},
               'e':
                   {blank: (1, R, 'f')},
               'f':
                   {blank: (None, R, 'b')}}

# print(TuringMachine('0', transitions).list_complete_configuration())
#
# print(TuringMachine('0', transitions, initial_tape=[]).list_complete_configuration())

test = TuringMachine('b', transitions, initial_tape=[])
# for s in test.tape:
#     print(test.list_complete_configuration())
#     test.step()

test.reset()
while len(test.tape) < 20:
    print(test.str_complete_configuration())
    test.step()

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








