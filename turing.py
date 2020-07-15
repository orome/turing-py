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


# TBD - Improve format documentation
# m-configs and symbols are one char (ints tolerated for symbols)
# valid m-configs and sybols are those (inferred) from transitions
# simply makes no change to the complete configuration if no matching rule is found (unless debugging)
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

_HIGHLIGHT_SYMBOL = "\u001b[44m\u001b[37;1m" #"\u001b[44m\u001b[36;1m"
_HIGHLIGHT_M_CONFIG = "\u001b[44m\u001b[37;1m" #"\u001b[43;1m\u001b[31;1m"
_HIGHLIGHT_RESET = "\u001b[0m"


# TBD - Grow left
# TBD - Validaton of arguments and rules
# TBD - Check single character symbols and m_configurations for presentations that assume it
# TBD: Fix tape extention and associated copying; add both directions <<<
# REV - Add support for lists of m_configurations of  "else"/"any"/"all"; for now must explictly list
# TBD - Allow various ways of providing arguments to constructor
# TBD - Support richer m_configuration labels (e.g. as comments)
# TBD - Better formatting of comments with tape/config; as new output form or option to str_ functions in class <<<
# TBD - Expand display_text() with decoration, highlight, arguments, comment on additiona line, long state name, etc.
# TBD - Pull highlightint out into seperate utility <<<
# TBD - Graphic/matplotlib version of display_text
# TBD - CLI
# TBD - Skeleton tables

# TBD - Behavior and transition format and argument requirements <<<


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

    # TBD - Expand with decoration, highlight, arguments
    # TBD - Pull higlighting out into own utility function
    def display_text(self) -> str:
        tape = list(self.str_tape())
        annotation = [' '] * len(tape)
        tape[self._position] = _HIGHLIGHT_SYMBOL + tape[self._position] + _HIGHLIGHT_RESET
        annotation[self._position] = _HIGHLIGHT_M_CONFIG + self._m_configuration + _HIGHLIGHT_RESET
        return ''.join(tape) + '\n' + ''.join(annotation)

    def step(self, debug: bool = False) -> None:
        # Providing a simple tuple is allowed; force to Behavior
        # REV - Remove if Behavior is strictly required
        try:
            behavior = Behavior(*self.transitions[self._m_configuration][self._tape[self._position]])
        # REV - Better way of detecting missing behavior for current m_config or current symbol
        except KeyError:
            if debug:
                # If debugging, treat absense of a behavior for the current configuration as an error
                try:
                    self.transitions[self._m_configuration]
                except KeyError:
                    raise UnknownMConfig(self._m_configuration)
                try:
                    self.transitions[self._m_configuration][self._tape[self._position]]
                except KeyError:
                    raise UnknownSymbol(self._tape[self._position])
            else:
                # If not debugging, do nothing if no behavior matching the current configuration is found
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




# ======== Some errors

class TuringError(Exception):
    def __init__(self, bad_token: chr = '') -> None:
        self.bad_token = bad_token


class UnknownSymbol(TuringError):
    """An encountered symbol is not present in the recognized configurations in the transition table."""

    def __str__(self) -> str:
        return str('Unrecognized symbol: {0}'.format(self.bad_token))


class UnknownMConfig(TuringError):
    """An encountered m-configuration is not present in the recognized configurations in the transition table."""

    def __str__(self) -> str:
        return str('Unrecognized m-configuration: {0}'.format(self.bad_token))


class BadToken(TuringError):
    """An m-confugration or symbol is not a single character or string of length 1."""

    def __str__(self) -> str:
        return str('Invalid toekn: {0}'.format(self.bad_token))
