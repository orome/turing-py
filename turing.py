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
from enum import IntEnum, Enum
from copy import deepcopy
from sys import exit


class Step(IntEnum):
    L = -1
    R = +1
    N = 0


# TBD - Make Enum; what is pythonic way do to this so arguments can be the string values? <<<
# class Representation(Enum):
#     SD = 'SD'
#     DN = 'DN'
Representation =str

FORMAT_CHARS = {
    'SD':
        {'m_config_base': 'D', 'm_config_index': lambda i: i*'A',
         'symbol_base': 'D', 'symbol_index': lambda i: i*'C',
         Step.N: 'N', Step.R: 'R', Step.L: 'L',
         'seperator': ';'},
    'DN':
        {'m_config_base': '3', 'm_config_index': lambda i: i*'1',
         'symbol_base': '3', 'symbol_index': lambda i: i*'2',
         Step.N: '6', Step.R: '5', Step.L: '4',
         'seperator': '7'},
    'tuples':   # REV - Chage to 'tuple' ?
        {'m_config_base': 'q', 'm_config_index': lambda i: str(i),
         'symbol_base': 'S', 'symbol_index': lambda i: str(i),
         Step.N: 'N', Step.R: 'R', Step.L: 'L',
         'seperator': ';'},
    'YAML':
        {Step.R: 'R' ,Step.L: 'L', Step.N: 'N',
         'seperator': '\n'}
}

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


# REV - Allow Behavior to be alternately specified as just a tuple (coerced when used)
# REV - Better name <<<
Transitions = Dict[MConfig, Dict[Union[Symbol,Tuple[Symbol]], Union[Behavior,tuple]]]


# TBD - Way to override <<<
E = ' ' # E for "empty"

L = Step.L
R = Step.R
N = Step.N

# See for how these look on various platforms - https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
_HIGHLIGHT_SYMBOL = "\u001b[44m\u001b[37;1m"    # "\u001b[44m\u001b[36;1m"
_HIGHLIGHT_M_CONFIG = "\u001b[44m\u001b[37;1m"  # "\u001b[43;1m\u001b[31;1m"
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
# TBD - Reorganize tape as function like transitions, with various representations <<<
# TBD - CLI
# TBD - Add tabular formats for transisions <<<
# TBD - Note where Turing conventions are assumed/enforced (eg one direction, single character symbols); opt disable
# TBD - Force single character symbol. Allow multi character state, add display for multi character state
# TBD - Warn in docs that multi character state may not work with some representations
# TBD - Skeleton tables
# TBD - Further examples
#       Universal Turing Machine: https://link.springer.com/content/pdf/bbm%3A978-1-84882-555-0%2F1.pdf
#       Square root of 2 program (and accuracy test) - https://www.math.utah.edu/~pa/math/q1.html
# TBD - Add unit tests
# TBD - Puzzle: find another member of the pattern Description number -> Output
# TBD - Convert transitions to standard form
# TBD - Save entire previous behavior (not just self._step_comment); use in new display (e.g. tuple for last used rule)
# TBD - Export MMA format
# TBD - Import / export turingmachine.io format
# TBD - Allow providing transtions as DN or SD: generate transition dict from them
# TBD - Support alternate names for the various representations (SD, DN, etc.)
# TBD - Use representations (e.g. SD encoding) for tape and complete configurations as well
# REV - Copy arguments provided as lists (e.g. symbol_ordering)

# TBD - Document behavior and transition format and argument requirements <<<


# ======== A simple Turing machine class

class TuringMachine(object):

    def __init__(self, initial_m_configuration: MConfig, transitions: Transitions,
                 initial_tape: Union[Tape, str] = str(E), initial_position: int = 0,
                 symbol_ordering: list = None, m_config_ordering: list = None,
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
        # REV - Copy necessary?
        self._transitions = deepcopy(processed_transitions)
        # TBD - Add ability to set other than defaults with optional arguments
        self._initial_position = initial_position

        # Ordering of symbols for various representations (e.g. S.D.)
        # Default config ordering is ordering of m-configurations in transitions
        if symbol_ordering is None:
            self._symbol_ordering = [E, '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        if m_config_ordering is None:
            self._m_config_ordering = self._transitions.keys()

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
            behavior = Behavior(*self._transitions[self._m_configuration][self._tape[self._position]])
        # REV - Better way of detecting missing behavior for current m_config or current symbol
        except KeyError:
            if debug:
                # If debugging, treat absense of a behavior for the current configuration as an error
                try:
                    self._transitions[self._m_configuration]
                except KeyError:
                    raise UnknownMConfig(self._m_configuration)
                try:
                    self._transitions[self._m_configuration][self._tape[self._position]]
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
            # Stop generating steps if the complete configuration has not changed
            if auto_halt:
                if (self._prev_tape == self._tape and
                        self._prev_m_configuration == self._m_configuration and
                        self._prev_position == self._position):
                    return
            yield self
            step += 1

    def _format_m_configuration(self, m_config: MConfig, representation: Representation) -> str:
        # m_config_indices = {}
        # for pos, m_cfg in enumerate(self._m_config_ordering):
        #     m_config_indices[m_cfg] = pos + 1
        m_config_indices = {m_cfg: pos+1 for pos, m_cfg in enumerate(self._m_config_ordering)}
        return FORMAT_CHARS[representation]['m_config_base'] + \
               FORMAT_CHARS[representation]['m_config_index'](m_config_indices[m_config])

    def _format_symbol(self, symbol: Symbol, representation: Representation) -> str:
        # symbol_indicies = {}
        # for pos, sym in enumerate(self._symbol_ordering):
        #     symbol_indicies[sym] = pos
        symbol_indicies = {sym:pos for pos, sym in enumerate(self._symbol_ordering)}
        return FORMAT_CHARS[representation]['symbol_base'] + \
               FORMAT_CHARS[representation]['symbol_index'](symbol_indicies[symbol])

    def _format_move(self, move: Step, representation: Representation) -> str:
        return FORMAT_CHARS[representation][move]

    def _format_seperator(self, representation: Representation) -> str:
        return FORMAT_CHARS[representation]['seperator']

    # TBD -- Tidy looping and names <<<
    # REV - Assumes transitions are in standard form
    def _transitions_list(self, representation: Representation = None) -> list:
        transition_representations = []
        if representation in ['SD', 'DN', 'tuples']:
            for m_config_start in self._transitions.keys():
                for scanned_symbol in self._transitions[m_config_start].keys():
                    behavior = Behavior(*self._transitions[m_config_start][scanned_symbol])
                    written_symbol = behavior.ops[0]
                    move = behavior.ops[1]
                    m_config_end = behavior.final_m_config
                    transition_representations.append(self._format_m_configuration(m_config_start, representation) +
                                                      self._format_symbol(scanned_symbol, representation) +
                                                      self._format_symbol(written_symbol, representation) +
                                                      self._format_move(move, representation) +
                                                      self._format_m_configuration(m_config_end, representation))
        # BUG - Use on https://turingmachine.io fails - https://github.com/aepsilon/turing-machine-viz/issues/6
        elif representation in ['YAML']:
            transition_representations.append('table:')
            for m_config_start in self._transitions.keys():
                transition_representations.append('\t{0}:'.format(m_config_start))
                for scanned_symbol in self._transitions[m_config_start].keys():
                    behavior = Behavior(*self._transitions[m_config_start][scanned_symbol])
                    written_symbol = behavior.ops[0]
                    move = behavior.ops[1]
                    m_config_end = behavior.final_m_config
                    transition_representations.append("\t\t\'{0}\': {{write: \'{1}\', {2}: {3}}}".format(
                        scanned_symbol,
                        written_symbol,
                        self._format_move(move, representation),
                        m_config_end))
        return transition_representations

    def transitions(self, representation: Representation = None, as_list: bool = False) -> Union[Transitions, list, str]:
        if representation in ['SD', 'DN', 'tuples', 'YAML']:
            # TBD - Coerce to standard representation names before calling _transitions_list
            if not as_list:
                return self._format_seperator(representation).join(self._transitions_list(representation) + [''])
            else:
                return self._transitions_list(representation)
        else:
            return deepcopy(self._transitions)


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
