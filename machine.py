#!/usr/bin/env python
# encoding: utf8

""" 
A simple Turing Machine implementation aimed at simulating the machines in Turing's 1936 paper.

.. note::
    Any additional note.
"""

from __future__ import annotations

import collections
import re
from typing import Union, NamedTuple
from enum import IntEnum
from copy import deepcopy
# from sys import exit


class Step(IntEnum):
    L = -1
    R = +1
    N = 0

    def __str__(self) -> str:
        return {N: 'N', R: 'R', L: 'L'}[self]


L = Step.L
R = Step.R
N = Step.N

# TBD - Make Enum; what is pythonic way do to this so arguments can be the string values? <<<
# class Representation(Enum):
#     SD = 'SD'
#     DN = 'DN'
InstructionFormat = str
TableFormat = str

# TBD - Rename <<<
FORMAT_CHARS = {
    'SD':
        {'symbol_format_fn': lambda i: 'D' + i*'C',
         'm_config_format_fn': lambda i: 'D' + (i + 1)*'A',
         'step_format_fn': lambda i: {Step.N: 'N', Step.R: 'R', Step.L: 'L'}[i],
         'separator': '', 'table_begin': '', 'table_end': ''},
    'DN':
        {'symbol_format_fn': lambda i: '3' + i * '2',
         'm_config_format_fn': lambda i: '3' + (i + 1) * '1',
         'step_format_fn': lambda i: {Step.N: '6', Step.R: '5', Step.L: '4'}[i],
         'separator': '', 'table_begin': '', 'table_end': ''},
    'tuples':   # REV - Change to 'tuple' ?
        {'symbol_format_fn': lambda i: 'S' + str(i),
         'm_config_format_fn': lambda i: 'q' + str(i + 1),
         'step_format_fn': lambda i: {Step.N: 'N', Step.R: 'R', Step.L: 'L'}[i],
         'separator': '', 'table_begin': '', 'table_end': ''},
    'wolfram':
        {'symbol_format_fn': lambda i: str(i),
         'm_config_format_fn': lambda i: str(i + 1),
         'step_format_fn': lambda i: i,
         'separator': ', ', 'table_begin': '{ ', 'table_end': ' }'},
    'YAML':
        {'step_format_fn': lambda i: {Step.N: 'N', Step.R: 'R', Step.L: 'L'}[i],
         'separator': '\n', 'table_begin': '', 'table_end': ''}
}

FORMAT_INSTRUCTION = {
    'SD': "{fmt_m_config_start}{fmt_scanned_symbol}{fmt_written_symbol}{fmt_move}{fmt_m_config_end};",
    'DN': "{fmt_m_config_start}{fmt_scanned_symbol}{fmt_written_symbol}{fmt_move}{fmt_m_config_end}7",
    'tuples': "{fmt_m_config_start}{fmt_scanned_symbol}{fmt_written_symbol}{fmt_move}{fmt_m_config_end};",
    'wolfram': "{{{fmt_m_config_start},  {fmt_scanned_symbol}}} ->  {{{fmt_m_config_end},  {fmt_written_symbol}, {fmt_move}}}"
}


# TBD - Improve format documentation
# symbols are one char
# m-configs are strings (though some representations will be hard to read with m-configs longer than one character
# valid m-configs and symbols are those (inferred) from instructions
# simply makes no change to the complete configuration if no matching rule is found (unless debugging)
Symbol = chr
MConfig = str
Tape = list[Symbol]
CompleteConfig = list[Union[Symbol, MConfig]]    # TBD - Limit to one MConfig?
Operations = list[Union[Step, Symbol]]


# If the from of ops is [Symbol, Step] then the Behavior is in standard form.
# TBD - Make class and move string method here <<<
class Behavior(NamedTuple):
    ops: Operations
    final_m_config: MConfig
    comment: str = ""

    @staticmethod
    def str_behavior(behavior: Behavior, show_comment: bool = False) -> str:
        # TBD - Fix to show blanks (quote strings), have choice of arrows, add comment, and omit first arrow <<<
        ops = behavior.ops if len(behavior.ops) > 0 else [N]
        operations = '?' if behavior is None else ','.join(
            [str(o) if isinstance(o, Step) else _HIGHLIGHT_WRITTEN_FMT.format(o) for o in ops])
        next_m_cfg = '?' if behavior is None else behavior.final_m_config
        comment = ('UNSPECIFIED' if behavior is None else
                   f"({behavior.comment})" if show_comment and behavior.comment != '' else '')
        return f"  →  {operations} | {next_m_cfg}  {comment}"

    def __str__(self) -> str:
        return Behavior.str_behavior(self)


E = ' '     # E for "empty"
F_SYMBOLS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
E_SYMBOLS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

# See for how these look on various platforms - https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
_HIGHLIGHT_SYMBOL_FMT = "|{}|"  # "\u001b[44m\u001b[37;1m{}\u001b[0m"
_HIGHLIGHT_M_CONFIG_FMT = _HIGHLIGHT_SYMBOL_FMT   # "\u001b[44m\u001b[37;1m{}\u001b[0m"
_HIGHLIGHT_ANNOTATION_FMT = "{}"
_HIGHLIGHT_WRITTEN_FMT = "\u001b[4m{}\u001b[24m"

# TBD - Isolate messy instructions for parsing in Instructions class. Same with tape. Deal with encoding stuff better. <<<
# !!! - Definition of alternating machine puts a step where a symbol should be (or vice versa) Still true??
# TBD - Fix utils.print_over to handle overwriting of variable number of lines <<<
# TBD - Fix _instructions_table so that it doesn't rely on lists, tidy _instructions_str now that it does not have to deal with tables <<<
# TBD - Fix places where private functions are being used; tidy up properties <<<
# TBD - Better differentiate handling of representations that don't work as lists of instructions vs those that do <<<
# TBD - Option to print blank differently <<<
# TBD - Representation as table (in various ways) <<<
# TBD - Handle tape representations in parallel with instructions; make sure formatting defs are in the right place <<<

# TBD - Catch places where standard form is required; test reordering with machine in standard form <<<
# TBD - Convert instructions to standard form <<<
# TBD - Add list of manipulations/transformations (add no ops, explicit match, etc.) as args to Transitions constructor <<<
# !!! - Fix no op writes in no op operations; see how this is done in Turing <<<
# TBD - Where add_no_op_instructions is handled, set a property; check where required true (e.g. wolfram representation) <<<
# TBD - Import turingmachine.io format <<<
# TBD - Import Wolfram format <<<
# REV - Decide whether to handle tuples and leave the provided dict unchanged
# TBD - Fix adding no op instructions to use explicit_configs and to handle entirely missing initial_m_config <<<
# TBD - Enforce / check standard form <<<
# TBD - Implement _is_long_moves and handle in display
# TBD - Add unit tests and reorganize tests (use example from Enigma project) <<<
# TBD - Better formatting of comments with tape/config; as new output form or option to str_ functions in class <<<
# TBD - Expand display_text() with decoration, highlight, arguments, comment on additional line, long state name, etc.
# TBD - Pull highlighting out into separate utility <<<
# TBD - Reorganize tape as function like instructions, with various representations <<<
# TBD - Add tabular formats for transitions <<<
# TBD - Save entire previous behavior (not just self._step_comment); use in new display (e.g. tuple for last used rule)
# TBD - Redo formatting for symbols, etc, to be more general
# TBD - Use representations (e.g. SD encoding) for tape and complete configurations as well
# TBD - Add better handling (detection and marking?) of display for multi character m-configurations
# TBD - Grow left; fix mishandling of blank on left (see test)
# TBD - Note where Turing conventions are assumed/enforced (eg one direction, single character symbols); opt disable
# TBD - Decide how to enforce conventions
# TBD - Add support for E and F squares; note as convention; opt for no erasures of F squares
# TBD - Document behavior and instruction format and argument requirements
# TBD - Use "configuration" (m-config + scanned symbol) in names and docs, check use of config vs m_config
# TBD - Validation of arguments and rules
# TBD - Warn in docs that multi character state may not work with some representations
# TBD - Skeleton tables
# TBD - Generalize and clean up dict_from_representation, especially splitting up of instructions into m_configs and ops
# TBD - Add alternate representation for blank (e.g. underline)
# TBD - Further examples
#       Universal Turing Machine: https://link.springer.com/content/pdf/bbm%3A978-1-84882-555-0%2F1.pdf
#       Square root of 2 program (and accuracy test) - https://www.math.utah.edu/~pa/math/q1.html
#       Implement representations on pp 146 and 148 <<<
# TBD - Change handling of YAML to generate JSON (listable?) and then convert to YAML for non list output
# TBD - Support dict_from_representation for YAML/JSON and wolfram (assert no long moves)
# TBD - CLI
# TBD - Graphic/matplotlib version of display_text
# TBD - Support alternate names for the various representations (SD, DN, etc.)
# TBD - Allow various ways of providing arguments to constructor
# TBD - Check single character symbols and m_configurations for presentations that assume it
# TBD - Puzzle: find another member of the pattern Description number -> Output
# TBD - Terms for: behavior provided for all configurations (even no ops), behavior = one move on char, one char match
#       Ask on SE, add her and in Automata doc <<<
#       Use terms above in names and docs
# REV - Copy arguments provided as lists (e.g. symbol_ordering)
# REV - Add support for lists of m_configurations of  "else"/"any"/"all"; for now must explicitly list
# REV - Force ints to chrs in creating processed instructions?
# REV - Allow providing of alternate single symbol m-mconfig (for some presentations)?


# instructionsDict are dictionaries of the form
#   {start_m_config: {matched_character_1: behavior_1, ...}}
# where for convenience, matched_character_1 can be a tuple of matched characters, and the behaviors may be provided
# as tuples rather than Behaviors.
# Where tuples of matched characters are provided, these will be replaced with one entry of the form above for each
# character in the tuple. If all provided behaviors are in standard form, then self._is_standard_form == True.
# REV - Allow Behavior to be alternately specified as just a tuple (coerced when used)

InstructionsDict = dict[MConfig, dict[Union[Symbol, tuple[Symbol]], Union[Behavior, tuple]]]


class Table(object):
    def __init__(self, instructions: Union[InstructionsDict, int, str],
                 e_symbol_ordering: list = None, m_config_ordering: list = None,
                 add_no_op_instructions: bool = False,
                 *args, **kw):

        if isinstance(instructions, int):
            instructions = self.dict_from_representation(instructions, 'DN', e_symbol_ordering, m_config_ordering)
        elif isinstance(instructions, str):
            instructions = self.dict_from_representation(instructions, 'SD', e_symbol_ordering, m_config_ordering)

        # These may turn false in the examination below
        self._is_one_write_max = True
        self._is_explicit_write = True
        self._is_standard_form = True   # TBD: Enforce
        # This is enforced below
        # REV - Decide whether to handle tuples and leave the provided dict unchanged <<<
        self._is_single_symbol_match = True
        # This optionally enforced below, or may change on examination
        self._is_explicit_configs = True
        # TBD - Implement <<<
        self._is_long_moves = False

        m_configs_from_instructions = list(instructions.keys())
        symbols_from_instructions = {E}

        # Go through the instructions and find symbols and m_configs, reorganize to have one symbol match per rule,
        # Determine if _is_standard_form, _is_one_write_max, and thus _is_standard_form
        # Also make sure every behavior is a Behavior
        processed_instructions = deepcopy(instructions)
        for m_config in instructions.keys():
            for syms in instructions[m_config].keys():
                # Collect all symbols and m-configurations used mentioned in instructions
                for sym in tuple(syms):
                    symbols_from_instructions.add(sym)
                behavior = Behavior(*instructions[m_config][syms])
                processed_instructions[m_config][syms] = behavior
                ops = behavior.ops

                self._is_one_write_max = (self._is_one_write_max and
                                          (sum(map(lambda o: not isinstance(o, Step), ops)) == 0 or
                                          (sum(map(lambda o: not isinstance(o, Step), ops)) == 1 and
                                           not isinstance(ops[0], Step))))
                self._is_explicit_write = (self._is_explicit_write and
                                           len(ops) != 0 and not isinstance(ops[0], Step))

                self._is_standard_form = (self._is_standard_form and
                                          len(ops) == 2 and self._is_one_write_max and self._is_explicit_write)

                # self._is_standard_form = (self._is_one_write_max and len(ops) == 2 and
                #                           not isinstance(ops[0], Step) and isinstance(ops[1], Step))
                for op in ops:
                    if not isinstance(op, Step):
                        symbols_from_instructions.add(op)
                final_m_config = behavior.final_m_config
                if final_m_config not in m_configs_from_instructions:
                    # Order encountered matters for convention, so append rather than add
                    m_configs_from_instructions.append(final_m_config)
                # Where multiple read symbols are listed, replace with one rule for each, for ease of later indexing
                # REV - Decide whether to handle tuples and leave the provided dict unchanged <<<
                if isinstance(syms, tuple):
                    for sym in syms:
                        processed_instructions[m_config][sym] = Behavior(*behavior)
                    del (processed_instructions[m_config][syms])

        # !!! - Must be in standard form to work <<<
        # Add any missing no-op rules and expand empty ones (e.g. required for valid Wolfram TuringMachine)

        # TBD - Fix to use _is_explicit_configs and to handle entirely missing initial_m_config <<<
        if add_no_op_instructions:
            for m_config in processed_instructions.keys():
                for sym in symbols_from_instructions:
                    if sym not in processed_instructions[m_config].keys():
                        processed_instructions[m_config][sym] = Behavior([sym, N], m_config, "No-op")
                    # TBD - Pythonic way to change just one of the named parameters
                    elif not processed_instructions[m_config][sym].ops:
                        processed_instructions[m_config][sym] = Behavior([sym, N],
                                                                         processed_instructions[
                                                                             m_config][sym].final_m_config,
                                                                         processed_instructions[m_config][sym].comment)

        # REV - Copy necessary?
        self._instructions = deepcopy(processed_instructions)

        # Ordering of symbols for various representations (e.g. S.D.)
        if e_symbol_ordering is None:
            # Default symbol ordering is sorted
            self._symbol_ordering = sorted(list(symbols_from_instructions))
        else:
            # If E-symbol ordering is blank, sorted F-symbols, provided E-symbol ordering
            self._symbol_ordering = [E] + sorted(
                filter(lambda s: s in F_SYMBOLS, symbols_from_instructions)) + e_symbol_ordering.copy()
        assert sorted(self._symbol_ordering) == sorted(symbols_from_instructions), "Ordering of symbols is incomplete"

        if m_config_ordering is None:
            # Default m-configuration ordering is as encountered in provided instructions
            self._m_config_ordering = m_configs_from_instructions
        else:
            # If m-config ordering is specified, that is used
            self._m_config_ordering = m_config_ordering.copy()
        assert sorted(self._m_config_ordering) == sorted(
            m_configs_from_instructions), "Ordering of m-configs is incomplete"

    @staticmethod
    def dict_from_representation(instruction_rep: Union[int, str], representation: InstructionFormat,
                                 m_config_ordering: list = None,
                                 e_symbol_ordering: list = None, f_symbol_num: int = 2) -> InstructionsDict:

        if isinstance(instruction_rep, int):
            assert representation == 'DN'
            instruction_rep = str(instruction_rep)

        # TBD - Assert valid representation; at least check what symbols are in it.

        if not e_symbol_ordering:
            e_symbol_ordering = E_SYMBOLS
        symbol_ordering = [E] + [str(f) for f in range(f_symbol_num)] + e_symbol_ordering.copy()

        if not m_config_ordering:
            m_config_fmt_fn = FORMAT_CHARS['tuples']['m_config_format_fn']
        else:
            m_config_fmt_fn = lambda i: m_config_ordering[i]
        move_fmt_fn = FORMAT_CHARS[representation]['step_format_fn']
        move_fmt = {move_fmt_fn(i): i for i in [N, R, L]}

        # REV - Find a better way to split up and match each row of the table
        delimiter = FORMAT_CHARS[representation]['symbol_format_fn'](0)
        instructions = instruction_rep.split(FORMAT_INSTRUCTION[representation][-1])[:-1]
        split_instructions = [re.split(delimiter,
                                       t.replace(move_fmt_fn(N), delimiter+move_fmt_fn(N)
                                                 ).replace(move_fmt_fn(R), delimiter+move_fmt_fn(R)
                                                           ).replace(move_fmt_fn(L), delimiter+move_fmt_fn(L)))[1:]
                              for t in instructions]

        instructions_dict = dict()
        for i, split_rule in enumerate(split_instructions):
            initial_m_config = m_config_fmt_fn(len(split_rule[0]) - 1)
            read_symbol = symbol_ordering[len(split_rule[1])]
            written_symbol = symbol_ordering[len(split_rule[2])]
            move = move_fmt[split_rule[3]]
            final_m_config = m_config_fmt_fn(len(split_rule[4]) - 1)
            if instructions_dict not in initial_m_config:
                instructions_dict[initial_m_config] = {}
            instructions_dict[initial_m_config][read_symbol] = Behavior([written_symbol, move], final_m_config,
                                                                        instructions[i])

        return deepcopy(instructions_dict)

    @property
    def dict(self) -> InstructionsDict:
        return self._instructions   # REV - Copy? <<<

    def behavior(self, m_config: MConfig, symbol: Symbol) -> Behavior:
        try:
            self._instructions[m_config]
        except KeyError:
            raise UnknownMConfig(m_config)
        try:
            self._instructions[m_config][symbol]
        except KeyError:
            raise UnknownSymbol(symbol)
        return self._instructions[m_config][symbol]

    # @staticmethod
    def _format_move(self, move: Step, representation: InstructionFormat) -> str:
        assert isinstance(move, Step)
        return FORMAT_CHARS[representation]['step_format_fn'](move)

    # @staticmethod
    def _format_separator(self, representation: InstructionFormat) -> str:
        return FORMAT_CHARS[representation]['separator']

    def _format_m_configuration(self, m_config: MConfig, representation: InstructionFormat) -> str:
        assert m_config in self._m_config_ordering
        m_config_indices = {m_cfg: pos for pos, m_cfg in enumerate(self._m_config_ordering)}
        return FORMAT_CHARS[representation]['m_config_format_fn'](m_config_indices[m_config])

    def _format_symbol(self, symbol: Symbol, representation: InstructionFormat) -> str:
        assert not isinstance(symbol, Step) and symbol in self._symbol_ordering
        symbol_indices = {sym: pos for pos, sym in enumerate(self._symbol_ordering)}
        return FORMAT_CHARS[representation]['symbol_format_fn'](symbol_indices[symbol])

    def _format_instruction(self, instruction_format: InstructionFormat,
                            m_config_start: MConfig, m_config_end: MConfig,
                            scanned_symbol: Symbol, written_symbol: Symbol,
                            move: Step
                            ) -> str:
        fmt_elements = {
            'fmt_m_config_start': self._format_m_configuration(m_config_start, instruction_format),
            'fmt_m_config_end': self._format_m_configuration(m_config_end, instruction_format),
            'fmt_scanned_symbol': self._format_symbol(scanned_symbol, instruction_format),
            'fmt_written_symbol': self._format_symbol(written_symbol, instruction_format),
            'fmt_move': self._format_move(move, instruction_format),
        }
        return FORMAT_INSTRUCTION[instruction_format].format(**fmt_elements)

    # TBD -- Tidy looping and names <<<
    def _instructions_list(self, instruction_format: InstructionFormat = None) -> list:
        assert instruction_format in ['SD', 'DN', 'tuples', 'wolfram'], \
            f"Not a listable instruction format: {instruction_format}"
        instruction_representations = []
        if instruction_format in ['SD', 'DN', 'tuples', 'wolfram']:
            assert self._is_standard_form
            for m_config_start in self._instructions.keys():
                for scanned_symbol in self._instructions[m_config_start].keys():
                    behavior = self._instructions[m_config_start][scanned_symbol]
                    written_symbol = behavior.ops[0]
                    move = behavior.ops[1]
                    m_config_end = behavior.final_m_config
                    instruction_representations.append(self._format_instruction(instruction_format,
                                                                                m_config_start, m_config_end,
                                                                                scanned_symbol, written_symbol,
                                                                                move))
        return instruction_representations

    def _instructions_str(self, instruction_format: InstructionFormat = None) -> str:
        assert instruction_format in ['SD', 'DN', 'tuples', 'wolfram'], \
            f"Instruction format cannot be represented as a string: {instruction_format}"
        return (FORMAT_CHARS[instruction_format]['table_begin'] +
                self._format_separator(instruction_format).join(self._instructions_list(instruction_format)) +
                FORMAT_CHARS[instruction_format]['table_end'])

    # REV - This isn't really a list of representations; allow as list at all (move to instructions?) <<<
    # REV - Must use spaces and not tabs - https://github.com/aepsilon/turing-machine-viz/issues/6
    # REV - Handle formatting better (read from file)
    def _instructions_table(self, instruction_format: InstructionFormat = None) -> str:
        instruction_representations = []
        if instruction_format in ['YAML']:
            assert self._is_standard_form
            instruction_representations.append('table:')
            for m_config_start in self._instructions.keys():
                instruction_representations.append('  {0}:'.format(m_config_start))
                for scanned_symbol in self._instructions[m_config_start].keys():
                    behavior = self._instructions[m_config_start][scanned_symbol]
                    written_symbol = behavior.ops[0]
                    move = behavior.ops[1]
                    m_config_end = behavior.final_m_config
                    instruction_representations.append("    \'{0}\': {{write: \'{1}\', {2}: {3}}}".format(
                        scanned_symbol,
                        written_symbol,
                        self._format_move(move, instruction_format),
                        m_config_end))
        return FORMAT_CHARS[instruction_format]['table_begin'] + \
               self._format_separator(instruction_format).join(instruction_representations) + \
               FORMAT_CHARS[instruction_format]['table_end']

    def instructions(self, instruction_format: InstructionFormat = None,
                     table_format: TableFormat = None) -> Union[InstructionsDict, list, str]:
        # !!! - Why wont the rest of this test work? <<<
        if instruction_format == 'YAML' or table_format == 'YAML':
            instruction_format = 'YAML'
            table_format = 'YAML'

        if instruction_format in ['SD', 'DN', 'tuples', 'YAML', 'wolfram']:
            if not self._is_standard_form:
                raise NonStandardConfiguration(
                    requirement="To represent instructions as {}, they must be in standard form".format(
                        instruction_format))
            if instruction_format not in ['SD', 'DN', 'tuples', 'wolfram'] and table_format in ['string', 'list']:
                raise NonListableTableFormat(
                    requirement="To represent table as {}, instruction format must be listable ({}) is not listable".format(table_format, instruction_format))
            if table_format == 'string':
                return self._instructions_str(instruction_format)
            if table_format in ['table', 'YAML']:
                return self._instructions_table(instruction_format)
            else:
                return self._instructions_list(instruction_format)
        else:
            return self.dict


# ======== A simple Turing machine class

class TuringMachine(object):

    def __init__(self, initial_m_configuration: MConfig, instructions: Union[InstructionsDict, Table],
                 initial_tape: Union[Tape, str] = E, initial_position: int = 0,
                 *args, **kw):

        # Process alternate forms for arguments (tape a string, tuple for matched symbols with same behavior)
        # REV - Lots of deepcopy which may not be needed
        if isinstance(initial_tape, str):
            initial_tape = list(initial_tape)

        # Store the Tape internally as a dict
        self._dict_initial_tape = collections.defaultdict(lambda: E)
        for position, symbol in enumerate(initial_tape):
            self._dict_initial_tape[position] = symbol
        self._initial_m_configuration = initial_m_configuration
        # REV - Copy necessary?
        if isinstance(instructions, Table):
            self._table = deepcopy(instructions)
        else:
            self._table = Table(instructions)
        # TBD - Add ability to set other than defaults with optional arguments
        self._initial_position = initial_position

        # TBD - Way to not have to repeat this (and avoid errors about setting outside of __init__?
        # self.reset()
        self._tape = self._dict_initial_tape.copy()
        self._m_configuration = self._initial_m_configuration
        self._position = self._initial_position
        self._step = 0
        self._step_comment = "Initial configuration"

    def reset(self) -> None:
        self._tape = self._dict_initial_tape.copy()
        self._m_configuration = self._initial_m_configuration
        self._position = self._initial_position
        self._step = 0
        self._step_comment = "Initial configuration"

    @property
    def tape(self) -> Tape:
        list_tape = []
        # REV - Is Turing's omission of the final blank intentional? - https://cs.stackexchange.com/q/128346/1210
        for i in range(min(self._tape.keys()), 1+max(self._position, max(self._tape.keys()))):
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

    def instructions(self, instruction_format: InstructionFormat = None,
                     table_format: str = 'string') -> Union[InstructionsDict, list, str]:
        return self._table.instructions(instruction_format, table_format)

    # TBD - Expand with decoration, highlight, arguments
    # TBD - Pull highlighting out into own utility function
    # Display a formatted version of the complete configuration, with optional highlighting and annotation
    def display_text(self, 
                     show_step: bool = False,  # step_pad: tuple = (10, '0'),
                     symbol_highlight: str = None, m_config_highlight: str = None, annotations_highlight: str = None,
                     show_behavior: bool = False, show_comments: bool = False,
                     ) -> str:
        if symbol_highlight is None and m_config_highlight is None:
            symbol_highlight = _HIGHLIGHT_SYMBOL_FMT
            m_config_highlight = _HIGHLIGHT_M_CONFIG_FMT
        else:
            symbol_highlight = m_config_highlight if symbol_highlight is None else symbol_highlight
            m_config_highlight = symbol_highlight if m_config_highlight is None else m_config_highlight
        if annotations_highlight is None:
            annotations_highlight = _HIGHLIGHT_ANNOTATION_FMT

        tape_txt = list(self.str_tape())
        # m_config_txt = [' '] * len(tape_txt)
        tape_txt[self._position] = symbol_highlight.format(tape_txt[self._position])
        # m_config_txt[self._position] = m_config_highlight.format(self._m_configuration)

        rule_txt = annotations_highlight.format(
            Behavior.str_behavior(self._table.behavior(self._m_configuration, self._tape[self._position]),
                                  show_comments)) if show_behavior else ''

        m_config_txt = ' ' * self._position + m_config_highlight.format(self._m_configuration) + rule_txt
        display_lines = [''.join(tape_txt), ''.join(m_config_txt)]
        if show_step:
            # display_lines.insert(0, annotations_highlight.format(str(self._step).rjust(*step_pad)))
            display_lines.insert(0, ' ' * self._position + annotations_highlight.format(str(self._step)))
        return '\n'.join(display_lines)

    def step(self, debug: bool = False) -> None:
        try:
            behavior = self._table.behavior(self._m_configuration, self._tape[self._position])
            for op in behavior.ops:
                if isinstance(op, Step):
                    self._position += op
                else:
                    self._tape[self._position] = op
            self._m_configuration = behavior.final_m_config
            self._step_comment = behavior.comment
            self._step += 1
        except (UnknownMConfig, UnknownSymbol) as e:
            if debug:
                raise e

    # Sequential states of the machine, starting with the current state and leaving the machine in the last state
    def steps(self, steps: int = None, include_current: bool = True, reset: bool = True, extend: bool = False,
              auto_halt: bool = False, debug: bool = False) -> generator[TuringMachine, None, None]:
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


# ======== Some errors

class TuringError(Exception):
    def __init__(self, bad_token: str = '', requirement: str = '') -> None:
        self.bad_token = bad_token
        self.requirement = requirement


class UnknownSymbol(TuringError):
    """An encountered symbol is not present in the recognized configurations in the instruction table."""

    def __str__(self) -> str:
        return str('Unrecognized symbol: {0}'.format(self.bad_token))


class UnknownMConfig(TuringError):
    """An encountered m-configuration is not present in the recognized configurations in the instruction table."""

    def __str__(self) -> str:
        return str('Unrecognized m-configuration: {0}'.format(self.bad_token))


class BadToken(TuringError):
    """An m-configuration or symbol is not a single character or string of length 1."""

    def __str__(self) -> str:
        return str('Invalid token: {0}'.format(self.bad_token))


class NonStandardConfiguration(TuringError):
    """An encountered machine specification is not present in full standard form (where required)."""

    def __str__(self) -> str:
        return str('Machine specification not in standard form: {0}'.format(self.requirement))


class NonListableTableFormat(TuringError):
    """A non-listable table format requested as a list."""

    def __str__(self) -> str:
        return str('Requested table format is not listable: {0}'.format(self.requirement))
