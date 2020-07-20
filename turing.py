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
Representation = str

# TBD - Rename <<<
FORMAT_CHARS = {
    'SD':
        {'symbol_format_fn': lambda i: 'D' + i*'C',
         'm_config_format_fn': lambda i: 'D' + (i + 1)*'A',
         'step_format_fn': lambda i: {Step.N: 'N', Step.R: 'R', Step.L: 'L'}[i],
         'seperator': ';', 'table_begin': '', 'table_end': ''},
    'DN':
        {'symbol_format_fn': lambda i: '3' + i * '2',
         'm_config_format_fn': lambda i: '3' + (i + 1) * '1',
         'step_format_fn': lambda i: {Step.N: '6', Step.R: '5', Step.L: '4'}[i],
         'seperator': '7', 'table_begin': '', 'table_end': ''},
    'tuples':   # REV - Chage to 'tuple' ?
        {'symbol_format_fn': lambda i: 'S' + str(i),
         'm_config_format_fn': lambda i: 'q' + str(i + 1),
         'step_format_fn': lambda i: {Step.N: 'N', Step.R: 'R', Step.L: 'L'}[i],
         'seperator': ';', 'table_begin': '', 'table_end': ''},
    'wolfram':
        {'symbol_format_fn': lambda i: str(i),
         'm_config_format_fn': lambda i: str(i + 1),
         'step_format_fn': lambda i: {Step.N: 0, Step.R: 1, Step.L: -1}[i],
         'seperator': ', ', 'table_begin': '{ ', 'table_end': ' }'},
    'YAML':
        {'step_format_fn': lambda i: {Step.N: 'N', Step.R: 'R', Step.L: 'L'}[i],
         'seperator': '\n', 'table_begin': '', 'table_end': ''}
}

FORMAT_TRANSITION = {
    'SD': "{fmt_m_config_start}{fmt_scanned_symbol}{fmt_written_symbol}{fmt_move}{fmt_m_config_end}",
    'DN': "{fmt_m_config_start}{fmt_scanned_symbol}{fmt_written_symbol}{fmt_move}{fmt_m_config_end}",
    'tuples':"{fmt_m_config_start}{fmt_scanned_symbol}{fmt_written_symbol}{fmt_move}{fmt_m_config_end}",
    'wolfram': "{{{fmt_m_config_start},  {fmt_scanned_symbol}}} ->  {{{fmt_m_config_end},  {fmt_written_symbol}, {fmt_move}}}"
}


# TBD - Improve format documentation
# m-configs and symbols are one char (ints tolerated for symbols)
# valid m-configs and sybols are those (inferred) from transitions
# simply makes no change to the complete configuration if no matching rule is found (unless debugging)
Symbol = chr
MConfig = chr
Tape = List[Symbol]
CompleteConfig = List[Union[Symbol, MConfig]]    # TBD - Limit to one MConfig?


# If the from of ops is [Symbol, Step] then the Behavior is in standard form.
class Behavior(NamedTuple):
    ops: List[Union[Step,Symbol]]
    final_m_config: MConfig
    comment: str = ""


# Transitions are dictionaries of the form
#   {start_m_config: {matched_character_1: behavior_1, ...}}
# where for convenience, matched_character_1 can be a tuple of matched characters, and the behaviors may be provided
# as tuples rather than Behaviors.
# Where tuples of matched characters are provided, these will be replaced with one entry of the form above for each
# character in the tuple. If all provided behaviors are in standard form, then self._is_standard_form == True.
# REV - Allow Behavior to be alternately specified as just a tuple (coerced when used)
# REV - Better name <<<
Transitions = Dict[MConfig, Dict[Union[Symbol,Tuple[Symbol]], Union[Behavior,tuple]]]


# TBD - Way to override <<<
E = ' ' # E for "empty"
F_SYMBOLS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

L = Step.L
R = Step.R
N = Step.N

# See for how these look on various platforms - https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
_HIGHLIGHT_SYMBOL = "\u001b[44m\u001b[37;1m"    # "\u001b[44m\u001b[36;1m"
_HIGHLIGHT_M_CONFIG = "\u001b[44m\u001b[37;1m"  # "\u001b[43;1m\u001b[31;1m"
_HIGHLIGHT_RESET = "\u001b[0m"


# !!! - Definition of alternating machine puts a step where a symbol should be (or vice versa) <<<<
# TBD - Catch places where standard form is required; test reording with machine in standard form <<<
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
# TBD - Redo formatting for symbols, etc, to be more genaral <<<
# TBD - Puzzle: find another member of the pattern Description number -> Output
# TBD - Convert transitions to standard form
# TBD - Save entire previous behavior (not just self._step_comment); use in new display (e.g. tuple for last used rule)
# TBD - Export MMA format
# TBD - Change handling of YAML to generalte JSON (listable) and then convert to YAML for non list output
# TBD - Import / export turingmachine.io format
# TBD - Allow providing transtions as DN or SD: generate transition dict from them
# TBD - Support alternate names for the various representations (SD, DN, etc.)
# TBD - Force ints to chrs in creating processed transitions
# TBD - Use representations (e.g. SD encoding) for tape and complete configurations as well
# REV - Copy arguments provided as lists (e.g. symbol_ordering)

# TBD - Document behavior and transition format and argument requirements <<<


# ======== A simple Turing machine class

class TuringMachine(object):

    def __init__(self, initial_m_configuration: MConfig, transitions: Transitions,
                 initial_tape: Union[Tape, str] = E, initial_position: int = 0,
                 e_symbol_ordering: list = None, m_config_ordering: list = None,
                 add_no_op_transitions: bool = False,
                 *args, **kw):

        # Process alternate forms for arguments (tape a string, tuple for matched symbols with same behavior)
        # REV - Lots of deepcopy which may not be needed
        if isinstance(initial_tape, str):
            initial_tape = list(initial_tape)

        self._is_standard_form = True
        symbols_from_transitions = set(initial_tape + [E])
        # List of m-configs captured from transitions, in order of rules, and then as additional final states found
        m_configs_from_transitons = list(transitions.keys())

        # Go through the transitions and find symbols and m_configs, reorganize to have one symbol match per rule,
        # Determine if the result is in standard form
        processed_transitions = deepcopy(transitions)
        for m_config in transitions.keys():
            for syms in transitions[m_config].keys():
                # Collect all symbols and m-configurations used mentioned in transitions
                for sym in tuple(syms):
                    symbols_from_transitions.add(sym)
                ops = transitions[m_config][syms][0]
                self._is_standard_form = (self._is_standard_form and len(ops) == 2 and
                                          not isinstance(ops[0], Step) and isinstance(ops[1], Step))
                for op in transitions[m_config][syms][0]:
                    if not isinstance(op, Step):
                        symbols_from_transitions.add(op)
                final_m_config = transitions[m_config][syms][1]
                if final_m_config not in m_configs_from_transitons:
                    # Order encountered matters for convention, so append rather than add
                    m_configs_from_transitons.append(final_m_config)
                # Where multiple read symbols are listed, replace with one rule for each, for ease of later indexing
                if isinstance(syms, tuple):
                    for sym in syms:
                        processed_transitions[m_config][sym] = transitions[m_config][syms]
                    del(processed_transitions[m_config][syms])

        # Add any missing no-op rules (e.g. required for valid Wolfram TuringMachine
        if add_no_op_transitions:
            for m_config in processed_transitions.keys():
                for sym in symbols_from_transitions:
                    if sym not in processed_transitions[m_config].keys():
                        processed_transitions[m_config][sym] = Behavior([sym, N], m_config)

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
        if e_symbol_ordering is None:
            # Default symbol ordering is sorted
            self._symbol_ordering = sorted(list(symbols_from_transitions))
        else:
            # If E-symbol ordering is specified ordering is blank, sorted F-symbols, provided E-symbol ordering
            self._symbol_ordering = [E] + sorted(filter(lambda s: s in F_SYMBOLS, symbols_from_transitions)) + e_symbol_ordering.copy()
        assert sorted(self._symbol_ordering) == sorted(symbols_from_transitions), "Ordering of symbols is incomplete"

        if m_config_ordering is None:
            # Default m-configuration ordering is as encountered in provided transitions
            self._m_config_ordering = m_configs_from_transitons
        else:
            # If m-config ordering is specified, that is used
            self._m_config_ordering = m_config_ordering.copy()
        assert sorted(self._m_config_ordering) == sorted(m_configs_from_transitons), "Ordering of m-configs is incomplete"

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
        assert m_config in self._m_config_ordering
        m_config_indices = {m_cfg: pos for pos, m_cfg in enumerate(self._m_config_ordering)}
        return FORMAT_CHARS[representation]['m_config_format_fn'](m_config_indices[m_config])

    def _format_symbol(self, symbol: Symbol, representation: Representation) -> str:
        assert not isinstance(symbol, Step) and symbol in self._symbol_ordering
        symbol_indicies = {sym:pos for pos, sym in enumerate(self._symbol_ordering)}
        return FORMAT_CHARS[representation]['symbol_format_fn'](symbol_indicies[symbol])

    def _format_move(self, move: Step, representation: Representation) -> str:
        assert isinstance(move, Step)
        return FORMAT_CHARS[representation]['step_format_fn'](move)

    def _format_seperator(self, representation: Representation) -> str:
        return FORMAT_CHARS[representation]['seperator']

    def _format_transition(self, representation: Representation,
                           m_config_start: MConfig, m_config_end: MConfig,
                           scanned_symbol: Symbol, written_symbol: Symbol,
                           move: Step
                           ) -> str:
        fmt_elements = {
            'fmt_m_config_start': self._format_m_configuration(m_config_start, representation),
            'fmt_m_config_end': self._format_m_configuration(m_config_end, representation),
            'fmt_scanned_symbol': self._format_symbol(scanned_symbol, representation),
            'fmt_written_symbol': self._format_symbol(written_symbol, representation),
            'fmt_move': self._format_move(move, representation),
        }
        return format(FORMAT_TRANSITION[representation].format(**fmt_elements))

    # TBD -- Tidy looping and names <<<
    def _transitions_list(self, representation: Representation = None) -> list:
        transition_representations = []
        if representation in ['SD', 'DN', 'tuples', 'wolfram']:
            assert self._is_standard_form
            for m_config_start in self._transitions.keys():
                for scanned_symbol in self._transitions[m_config_start].keys():
                    behavior = Behavior(*self._transitions[m_config_start][scanned_symbol])
                    written_symbol = behavior.ops[0]
                    move = behavior.ops[1]
                    m_config_end = behavior.final_m_config
                    transition_representations.append(self._format_transition(representation,
                                                                              m_config_start, m_config_end,
                                                                              scanned_symbol, written_symbol,
                                                                              move))
        # BUG - Use on https://turingmachine.io fails - https://github.com/aepsilon/turing-machine-viz/issues/6
        # REV - This isn't really a list of representations; allow as list at all (move to transitions?) <<<
        elif representation in ['YAML']:
            assert self._is_standard_form
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
        if representation in ['SD', 'DN', 'tuples', 'YAML', 'wolfram']:
            if not self._is_standard_form:
                raise NonStandardConfiguration(
                    requirement="To represent as {}, transitions must be in standard form".format(representation))
            if not as_list:
                return FORMAT_CHARS[representation]['table_begin'] + \
                       self._format_seperator(representation).join(self._transitions_list(representation) + ['']) +\
                       FORMAT_CHARS[representation]['table_end']

            else:
                return self._transitions_list(representation)
        else:
            return deepcopy(self._transitions)


# ======== Some errors

class TuringError(Exception):
    def __init__(self, bad_token: chr = '', requirement: str = '') -> None:
        self.bad_token = bad_token
        self.requirement = requirement


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
        return str('Invalid token: {0}'.format(self.bad_token))


class NonStandardConfiguration(TuringError):
    """An encountered machnine specification is not present in full standard form (where requried."""

    def __str__(self) -> str:
        return str('Machine specification not in standard form: {0}'.format(self.requirement))
