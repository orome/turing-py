#!/usr/bin/env python
# encoding: utf8

""" 
A simple Turing Machine implementation aimed at simulating the machines in Turing's 1936 paper.

.. note::
    Any additional note.
"""

from __future__ import annotations

import collections
from typing import List, Dict, Union, Tuple, NamedTuple, Generator
from enum import IntEnum
from copy import deepcopy
from sys import exit


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
    comment: str = ""


# REV - Allow Behavior to be alternatily spefified as just a tuple
Transitions = Dict[MConfig, Dict[Union[Symbol,Tuple[Symbol]], Union[Behavior,tuple]]]


# TBD - Way to override <<<
E = ' ' # E for "empty"

L = Step.L
R = Step.R
N = Step.N


# TBD - Grow left
# TBD - Validaton of arguments and rules
# TBD - Check single character symbols and m_configurations for presentations that assume it
# TBD: Fix tape extention and associated copying; add both directions <<<
# TBD - Add support for lists of m_configurations (with same behavior) in transitions
# TBD - Add support for lists of m_configurations of  "else"/"any"
# TBD - Allow various ways of providing arguments to constructor

class TuringMachine(object):

    def __init__(self, initial_m_configuration: MConfig, transitions: Transitions,
                 initial_tape: Union[Tape, str] = str(E), initial_position: int = 0,
                 *args, **kw):

        # Process alternate forms for arguments (tape a string, tuple for matched symbols with same behavior)
        # REV - Lots of deepcopy which may not be needed
        if isinstance(initial_tape, str):
            initial_tape = list(initial_tape)
        processed_transitions = deepcopy(transitions)
        for m_config in transitions.keys():
            for syms in transitions[m_config].keys():
                if isinstance(syms, tuple):
                    for sym in syms:
                        processed_transitions[m_config][sym] = transitions[m_config][syms]
                    del(processed_transitions[m_config][syms])

        # Store the Tape internally as a dict
        self._dict_initial_tape = collections.defaultdict(lambda : E)
        for position, symbol in enumerate(initial_tape):
            self._dict_initial_tape[position] = symbol
        self._initial_m_configuration = initial_m_configuration
        self.transitions = deepcopy(processed_transitions)
        # TBD - Add ability to set other than defaults with optional arguments
        self._initial_position = initial_position

        # TBD - Way to not have to repeat this (and avoid errors about setting outside of __init__?
        #self.reset()
        self._tape = self._dict_initial_tape.copy()
        self._m_configuration = self._initial_m_configuration
        self._position = self._initial_position
        self._step_comment = "Initial configuration"

    def reset(self) -> None:
        self._tape = self._dict_initial_tape.copy()
        self._m_configuration = self._initial_m_configuration
        self._position = self._initial_position
        self._step_comment = "Initial configuration"

    @property
    def tape(self) -> Tape:
        list_tape = []
        # REV - Is Turing's omission of the final blank intentional? - https://cs.stackexchange.com/q/128346/1210
        for i in range(0, 1+max(self._position, max(self._tape.keys()))):
            list_tape.append(self._tape[i])
        return list_tape

    @property
    def step_comment(self) -> str:
        return self._step_comment

    def complete_configuration(self) -> CompleteConfig:
        list_tape = self.tape
        list_tape.insert(self._position, self._m_configuration)
        return list_tape

    def str_tape(self) -> str:
        return ''.join([str(elem) for elem in self.tape])

    def str_complete_configuration(self) -> str:
        return ''.join([str(elem) for elem in self.complete_configuration()])

    def step(self, debug: bool = False) -> None:
        # Providing a simple tuple is allowed; force to Behavior
        # REV - Remove if Behavior is strictly required
        try:
            behavior = Behavior(*self.transitions[self._m_configuration][self._tape[self._position]])
        # REV - Better way of detecting missing behavior for current m_config or current symbol
        except KeyError:
            if debug:
                raise KeyError
            else:
                # Unless debugging, this do nothing if now matching behavior is found
                return
        for op in behavior.ops:
            if isinstance(op, Step):
                self._position += op
            else:
                self._tape[self._position] = op
        self._m_configuration = behavior.final_m_config
        self._step_comment = behavior.comment

    # Sequential states of the machine, starting with the current state and leaving the machine in the last state
    def steps(self, steps: int = None, include_current: bool = True, reset: bool = True, extend: bool = False,
              auto_halt: bool = False, debug: bool = False) -> Generator[TuringMachine, None, None]:
        if extend:
            reset = False
            include_current = False
        step = 0
        if reset:
            self.reset()
        if include_current:
            yield self
            step += 1
        while steps is None or step < steps:
            self._prev_tape = self._tape
            self._prev_m_configuration = self._m_configuration
            self._prev_position = self._position
            self.step(debug)
            if auto_halt:
                if (self._prev_tape == self._tape and
                        self._prev_m_configuration == self._m_configuration and
                        self._prev_position == self._position):
                    return
            yield self
            step += 1
        # else:
        #     return



    # # @tape.setter
    # def tape(self, t: dict) -> None:
    #     self._tape = t


# TBD- Some potential exceptions to throw
# class UnknownSymbol(Exception):
#     """This exception is raised when the Turing machine encounters a symbol
# that does not appear in the transition dictionary.
#     """
#     pass
#
#
# class UnknownState(Exception):
#     """This exception is raised when the Turing machine enters a state that
#     does not appear in the transition dictionary.
#     """
#     pass
#
#
# class BadSymbol(Exception):
#     """This exception is raised when the user attempts to specify a tape
#     alphabet that includes strings of length not equal to one.
#     """
#     pass

