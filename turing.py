#!/usr/bin/env python
# encoding: utf8

"""
Description

.. note::
    Any additional note.
"""

import argparse
from typing import List
from sys import exit
#from test import increasing  # TBD - MOVE <<<
import sys
import time

# TBD - Move to static class utilities <<<
def print_over(s, backup: bool = True, delay: float = 0.2) -> None:
    if backup:
        print('', end='\r')
        print("\033[F" * (s.count('\n')+2))
    print(s)
    sys.stdout.flush()
    time.sleep(delay)

# TBD - MOVE <<<



# from crypto_enigma import __version__
from machine import *



# ASK - What's idiomatic?
def fmt_arg(arg:str) -> str:
    return arg.upper()
    # return '<' + arg.lower() + '>'


def make_args(name: str, is_opt: bool = False, opt_letter: str = None) -> List[str]:
    if not is_opt:
        return [name]
    else:
        return ['--' + name, '-' + (opt_letter if opt_letter is not None else name[0])]


_HELP_ARGS = ['--help', '-h', '-?']
_HELP_KWARGS = dict(
    action='help',
    help='show this help message and exit')

_CONFIG_NAME = 'transitions'
_CONFIG_ARGS = make_args(_CONFIG_NAME)
_CONFIG_KWARGS = dict(
    action='store', metavar=fmt_arg(_CONFIG_NAME))

_TAPE_HELP = 'the initial tape; blank if omitted'
_ENCODE_TAPE_NAME = 'tape'
_ENCODE_TAPE_ARGS = make_args(_ENCODE_TAPE_NAME)
_ENCODE_TAPE_KWARGS = dict(
    action='store', metavar=fmt_arg(_ENCODE_TAPE_NAME),
    help=_TAPE_HELP)
_RUN_TAPE_ARGS = make_args(_ENCODE_TAPE_NAME, True)
_RUN_TAPE_KWARGS = dict(
    action='store', metavar=fmt_arg(_ENCODE_TAPE_NAME), nargs='?', default=' ', const=None,
    help=_TAPE_HELP)

_MCFG_HELP = 'the initial m-configuratin; first in orderin if omitted'
_ENCODE_MCFG_NAME = 'mconfig'
_ENCODE_MCFG_ARGS = make_args(_ENCODE_MCFG_NAME)
_ENCODE_MCFG_KWARGS = dict(
    action='store', metavar=fmt_arg(_ENCODE_MCFG_NAME),
    help=_MCFG_HELP)
_RUN_MCFG_ARGS = make_args(_ENCODE_MCFG_NAME, True)
_RUN_MCFG_KWARGS = dict(
    action='store', metavar=fmt_arg(_ENCODE_MCFG_NAME), nargs='?', default='q1', const=None,
    help=_MCFG_HELP)

_DISPLAY_GROUP_KWARGS = dict(
    title='display formatting arguments',
    description='optional arguments for controlling formatting of machine configurations')

_FORMAT_NAME = 'format'
_FORMAT_ARGS = make_args(_FORMAT_NAME, True)
_FORMAT_KWARGS = dict(
    action='store', metavar=fmt_arg(_FORMAT_NAME), nargs='?', default='single', const='single',
    help='the format used to display machine configuration(s) (see below)')

_HIGHLIGHT_NAME = 'highlight'
_HIGHLIGHT_ARGS = make_args(_HIGHLIGHT_NAME, True, 'H')
_HIGHLIGHT_KWARGS = dict(
    action='store', metavar=fmt_arg('hh'),
    help="a pair or characters to use to highlight encoded characters in a machine configuration's encoding "
         "(see below)")

_SHOWENCODING_NAME = 'showencoding'
_SHOWENCODING_ARGS = make_args(_SHOWENCODING_NAME, True, 'e')
_SHOWENCODING_KWARGS = dict(
    action='store_true',
    help='show the encoding if not normally shown for the specified ' + _FORMAT_KWARGS['metavar'])

_DESC = "A simple Enigma machine simulator with rich display of machine configurations."
_EXAMPLES = """\
Examples:

    $ %(prog)s run ...
    $ %(prog)s encode ...
    $ %(prog)s show ...

More information about each of these examples is available in the help for the respective
commands.

"""
_EPILOG = _EXAMPLES

# Run command help strings
_HELP_RUN = "show the operation of a Turing machine"
_DESC_RUN = """\
Show the operation of the Turing machine as a series of configurations, as it
encodes a message and/or for a specified number of steps.
"""
_EXAMPLES_RUN = """\
"""
_HELP_RUN_CONFIG = 'the transitions defining the machine (see below)'

# Version command help strings
_HELP_VERSION = 'show the package version and exit'
_DESC_VERSION = 'Show the package version and exit.'


_EPILOG_CONFIG = """\
{cfg_arg} specifies the transitions for the Turing machine, provided
as either a DN or an SD, with \';\' replaced by \'X\' to allow for entry
on the bash command line
"""

_EPILOG_FORMAT = """\
{fmt_arg} will determine the running machine is represented; possible values
include:
 + 'XXX' (the default) .
"""

_OPT_STRING_DEFAULT = """\
"""

# _EPILOG_ENCODE = _EPILOG_CONFIG + "\n" + _EXAMPLES_ENCODE
# _EPILOG_SHOW = _EPILOG_CONFIG + "\n" + _EPILOG_FORMAT + "\n" + _OPT_STRING_DEFAULT + "\n" + _EXAMPLES_SHOW
_EPILOG_RUN = _EPILOG_CONFIG + "\n" + _EPILOG_FORMAT + "\n" + _OPT_STRING_DEFAULT + "\n" + _EXAMPLES_RUN

_EPILOG_ARGS = dict(shw_cmd='show',
                    hgt_arg=_HIGHLIGHT_KWARGS['metavar'],
                    cfg_arg=_CONFIG_KWARGS['metavar'],
                    fmt_arg=_FORMAT_KWARGS['metavar']
                    # fmt_internal_val=EnigmaConfig._FMTS_INTERNAL[0],
)
# _EPILOG_ENCODE = _EPILOG_ENCODE.format(**_EPILOG_ARGS)
# _EPILOG_SHOW = _EPILOG_SHOW.format(opt_string_arg=_LETTER_KWARGS['metavar'], **_EPILOG_ARGS)
_EPILOG_RUN = _EPILOG_RUN.format(opt_string_arg=_RUN_TAPE_KWARGS['metavar'], **_EPILOG_ARGS)

# _TBD_TBD="""\
# a number of steps to run; if omitted, will run until the contents
# of the tape do not change, for a maximum of 100,000 steps
# """

if __name__ == '__main__':

    # ,
    # formatter_class = argparse.RawDescriptionHelpFormatter


    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--verbose', '-v',
                               action='store_true',
                               help='display additional information (may have no effect)')
    # REV - Doesn't like formatter_class
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description=_DESC, parents=[parent_parser],
                                     epilog=_EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     # usage = 'enigma.py [<options>] COMMAND CONFIG',
                                     add_help=False)
    parser.add_argument(*_HELP_ARGS, **_HELP_KWARGS)

    commands = parser.add_subparsers(help='', dest='command',
                                     # title='required arguments',
                                     # description='description, some commands to choose from',
                                     metavar=fmt_arg('command')
                                     )

    # Show machine operation
    run_parser = commands.add_parser('run', parents=[parent_parser], add_help=False,
                                     description=_DESC_RUN, epilog=_EPILOG_RUN, help=_HELP_RUN,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    _CONFIG_KWARGS['help'] = _HELP_RUN_CONFIG
    run_parser.add_argument(*_CONFIG_ARGS, **_CONFIG_KWARGS)
    run_input_group = run_parser.add_argument_group(title='initial configuration')
    run_input_group.add_argument(*_RUN_TAPE_ARGS, **_RUN_TAPE_KWARGS)
    run_input_group.add_argument(*_RUN_MCFG_ARGS, **_RUN_MCFG_KWARGS)

    # run_display_group = run_parser.add_argument_group(**_DISPLAY_GROUP_KWARGS)
    #run_display_group.add_argument(*_FORMAT_ARGS, **_FORMAT_KWARGS)
    #run_display_group.add_argument(*_HIGHLIGHT_ARGS, **_HIGHLIGHT_KWARGS)
    # run_display_group.add_argument(*_SHOWENCODING_ARGS, **_SHOWENCODING_KWARGS)

    run_operation_group = run_parser.add_argument_group(title='run operation arguments',
                                                        description='options for controlling stepping and '
                                                                    'annotation of steps')
    # REV - Rework using constants as for others? Revert to not using constants?
    run_operation_group.add_argument('--overwrite', '-O',
                                     action='store_true',
                                     help='overwrite each step after a pause '
                                          '(may result in garbled output on some systems)')
    run_operation_group.add_argument('--faster', '-F',
                                     action='count', default=0,
                                     help='slow down overwriting; '
                                          'repeat for more speed (only has effect with --overwrite)')
    run_operation_group.add_argument('--showstep', '-T', action='store_true',
                                     help='show the step number')
    run_operation_group.add_argument('--steps', '-S',
                                     action='store', metavar=fmt_arg('steps'), nargs='?', default=None, const=1,
                                     type=int,
                                     help='a number of steps to run; if omitted, will run until the contents'
                                          'of the tape do not change, for a maximum of 100,000 steps')
    run_operation_group.add_argument('--comment', '-C', action='store_true',
                                     help='show the comment for the last applied rule')
    run_parser.add_argument(*_HELP_ARGS, **_HELP_KWARGS)

    # Just show the package version
    version_parser = commands.add_parser('version', add_help=False,
                                         description=_DESC_VERSION + '.', help=_HELP_VERSION)
    version_parser.add_argument(*_HELP_ARGS, **_HELP_KWARGS)

    # try:
    #     args = parser.parse_args()
    # # ASK - How to catch just wrong argument errors <<<
    # # ASK - How to print help for current subcommand, if there is one <<<
    # except:# argparse.ArgumentError as e:
    #     parser.print_help()
    #     sys.exit(0)
    # else:

    args = parser.parse_args()

    try:
        #if args.command == 'version':
            # print('{0}'.format(__version__))

        # else:
            # uni_arg_err = "Unable to decode '{}' to Unicode; report this error!"

            #assert isinstance(args.config, str), uni_arg_err.format(_CONFIG_KWARGS['metavar'])
        #cfg = EnigmaConfig.config_enigma_from_string(args.config)
        #fmt = args.format

        if args.command == 'run':
            #assert isinstance(args.message, str), uni_arg_err.format(_ENCODE_TAPE_KWARGS['metavar'])
            transitions = args.transitions
            tape = args.tape

            # REV - Better processing
            transitions = transitions.replace('1', 'A').replace('2', 'C').replace('3', 'D').replace('4', 'L').replace('5', 'R').replace('6', 'N').replace('7', 'X')
            transitions = transitions.replace('X',';')
            # TBD - Handle other start states; provide ordered state list; support user defined state names
            # TBD - Handle other transitions besides DN and SD
            # TBD - Test initial tape as argument
            tt2 = TuringMachine(args.mconfig, Table(transitions), initial_tape=tape)
            print('\n')
            for i, q in enumerate(tt2.steps(1000000 if not args.steps else args.steps)):
                d = 0.2 - (0.05 * args.faster)
                s = f" ({i})" if args.showstep else ''
                c = f" {q.step_comment}"  if args.comment else ''
                # TBD - Pad to length of previoius to ensure overwrite! <<<
                print_over(q.display_text() + s + c, backup=args.overwrite, delay=(d if d > 0 else 0.01))
            print(args.mconfig)
        else:
            print(f"Command not implemented: {args.command}")
    except KeyboardInterrupt as e:
        # REV - Restore interrupt message and ask for trace?
        # if 'y' in raw_input('\rInterrupted by user; print stack trace? ').lower():
        #     traceback.print_exc()
        print('', end='\r')
        exit()
    except TuringError as e:
        print(e)  # TBD - Fix how TuringErrors report messages (to follow enigma) <<<
        exit(1)

