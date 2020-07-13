#!/usr/bin/env python
# encoding: utf8

""" 
A simple Turing Machine implementation aimed at simulating the machines in Turing's 1936 paper.

.. note::
    Any additional note.
"""

import collections
from typing import List, Dict, Union, Tuple, NamedTuple
from enum import IntEnum


class Step(IntEnum):
    L = -1
    R = +1
    N = 0


Symbol = chr
MConfig = chr
Tape = List[Symbol]
CompleteConfig = List[Union[Symbol, MConfig]]    # TBD - Limit to one MConfig?


class Behavior(NamedTuple):
    ops: List[Union[Step,Symbol]]
    final_m_config: MConfig


# REV - Allow Behavior to be alternatily spefified as just a tuple
Transitions = Dict[MConfig, Dict[Symbol, Union[Behavior,tuple]]]


blank = ' '

L = Step.L
R = Step.R
N = Step.N


# TBD - Support for versions on p. 84 and 87 of Petzold <<<
# TBD - Grow left
# TBD - Validaton
# TBD - Check single character symbols and m_configurations for presentations that assume it
# TBD: Fix tape extention and associated copying; add both directions <<<

class TuringMachine(object):

    def __init__(self, initial_m_configuration: MConfig, transitions: Transitions,
                 initial_tape: Tape = [blank], initial_position: int = 0,
                 #halt_state=100,
                 *args, **kw):
        # TBD - Process other kinds of arguments
        # Process tape provided as a list
        self._dict_initial_tape = collections.defaultdict(lambda : blank)
        for position, symbol in enumerate(initial_tape):
            self._dict_initial_tape[position] = symbol
        self._initial_m_configuration = initial_m_configuration
        self.transitions = transitions
        # TBD - Add ability to set other than defaults with optional arguments
        self._initial_position = initial_position

        self.reset()

    def reset(self) -> None:
        self._tape = self._dict_initial_tape.copy()
        self._m_configuration = self._initial_m_configuration
        self._position = self._initial_position

    # @property
    # def tape_dict(self) -> dict:
    #     return self._tape.copy()

    @property
    def tape(self) -> Tape:
        list_tape = []
        for i in range(0, 1+max(self._position, max(self._tape.keys()))):
            list_tape.append(self._tape[i])
        return list_tape
   
    def complete_configuration(self) -> CompleteConfig:
        list_tape = self.tape
        list_tape.insert(self._position, self._m_configuration)
        return list_tape

    def str_tape(self) -> str:
        return ''.join([str(elem) for elem in self.tape])

    def str_complete_configuration(self) -> str:
        return ''.join([str(elem) for elem in self.complete_configuration()])

    def step(self) -> None:
        # Behavior my just be a tuple
        behavior = Behavior(*self.transitions[self._m_configuration][self._tape[self._position]])
        for op in behavior.ops:
            if isinstance(op, Step):
                self._position += op
            else:
                self._tape[self._position] = op
        self._m_configuration = behavior.final_m_config


    # @tape.setter
    # def tape(self, t: dict) -> None:
    #     self._tape = t


# Petzold p. 81
alternate = {
    'b':
        {blank: (['0', R], 'c')},
    'c':
        {blank: ([R], 'e')},
    'e':
        {blank: (['1', R], 'f')},
    'f':
        {blank: ([R], 'b')}}

alternate_machine = TuringMachine('b', alternate, initial_tape=[blank])

for q in range(10):
    print(alternate_machine.tape)
    alternate_machine.step()

alternate_machine.reset()
for q in range(10):
    print(alternate_machine.str_complete_configuration())
    alternate_machine.step()


# Petzold p. 84
alternate2 = {
    'b':
        {blank: (['0'], 'b'),
         '0':   ([R, R, '1'], 'b'),
         '1':   ([R, R, '0'], 'b')}}

alternate_machine = TuringMachine('b', alternate2, initial_tape=[blank])

for q in range(10):
    print(alternate_machine.tape)
    alternate_machine.step()

alternate_machine.reset()
for q in range(10):
    print(alternate_machine.str_complete_configuration())
    alternate_machine.step()


# Petzold p. 87
increasing = {
    'b':
        {blank: (['ə', R, 'ə', R, '0', R, R, '0', L, L], 'o')},
    'o':
        {'1':   ([R,'x', L, L, L], 'o'),
         '0':   ([], 'q')},
    'q':
        {'1':   ([R, R], 'q'),      # TBD - A way to handle "any" <<<
         '0':   ([R, R], 'q'),
         blank: (['1', L], 'p')},
    'p':
        {'x':   ([blank, R], 'q'),
         'ə':   ([R], 'f'),
         blank: ([L, L], 'p')},
    'f':
        {'1': ([R, R], 'f'),    # TBD - A way to handle "any" <<<
         '0': ([R, R], 'f'),
         blank: (['0', L, L], 'o')},
}

increasing_machine = TuringMachine('b', increasing, initial_tape=[blank])

for q in range(50):
    print(increasing_machine.str_complete_configuration())
    increasing_machine.step()

increasing_machine.reset()
configuration = []
for q in range(8):
    configuration.append(increasing_machine.str_complete_configuration())
    increasing_machine.step()
print(':'.join(configuration))

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








