# Copyright (c) 2011-2012, 30loops.net
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of 30loops.net nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL 30loops.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Command line interface for the 30loops platform.
"""

import os
import json
import sys
import argparse
import ConfigParser


from simplethirty import utils
from libthirty.state import env
from simplethirty import actions
from libthirty.logbook import LogBookHandler

def ascii_art():
    art = """
    _____ _____ _                                    _
   |____ |  _  | |                                  | |
       / / |/' | | ___   ___  _ __  ___   _ __   ___| |_
       \ \  /| | |/ _ \ / _ \| '_ \/ __| | '_ \ / _ \ __|
   .___/ | |_/ / | (_) | (_) | |_) \__ \_| | | |  __/ |_
   \____/ \___/|_|\___/ \___/| .__/|___(_)_| |_|\___|\__|
                             | |
                             |_|
"""
    return art

class CommandError(Exception):
    pass

class CustomArgumentParser(argparse.ArgumentParser):
    """Override the default error method to hint more help to the user."""
    def error(self, message):
        self.print_usage()
        print >> sys.stderr, '\n'
        print >> sys.stderr, 'See "thirty help" for more information.'
        print >> sys.stderr, 'See "thirty help COMMAND" for help on a\
specific command.'
        sys.exit(1)


class ThirtyCommandShell(object):
    """The shell command dispatcher."""
    def get_base_parser(self):
        parser = CustomArgumentParser(
                prog="thirty",
                description=__doc__.strip(),
                epilog='See "thirty help COMMAND" '\
                       'for help on a specific command.',
                add_help=False
                )

        ###
        # Global arguments
        ###

        # Surpress the -h/--help command option
        parser.add_argument('-h', '--help',
            action='help',
            help=argparse.SUPPRESS)

        parser.add_argument("-u", "--username",
                action="store",
                metavar="<username>",
                help="The username that should be used for this request.")

        parser.add_argument("-p", "--password",
                action="store",
                metavar="<password>",
                help="The password to use for authenticating this request.")

        parser.add_argument("-a", "--account",
                action="store",
                metavar="<account>",
                help="The account that this user is a member of.")

        parser.add_argument("-r", "--uri",
                action="store",
                metavar="<uri>",
                default="https://api.30loops.net",
                help="Use <uri> as target URI for the 30loops platform.\
Normally you don't need that.")

        parser.add_argument("-i", "--api",
                action="store",
                metavar="<api>",
                default="1.0",
                help="The version of the api to use, defaults to 1.0.")

        parser.add_argument("-R", "--raw",
                action="store_true",
                default=False,
                help="Show the output as raw json.")

        return parser

    def get_subcommand_parsers(self, parser):
        """Populate the subparsers."""
        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar="<subcommand>")

        self._find_subcommands(subparsers)
        return parser

    def _find_subcommands(self, subparsers):
        """Find all subcommand arguments."""
        # load for each subcommands the appropriate shell file
        for f in os.listdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "actions"))):
            attr, ext = os.path.splitext(f)
            if ext == '.py' and not attr.startswith('_'):
                # make the commands have hyphens in place of underscores
                command = attr.replace('_', '-')
                callback = getattr(actions, attr)
                desc = callback.__doc__ or ''
                help = desc.strip().split('\n')[0]
                arguments = getattr(callback, 'arguments', [])

                subparser = subparsers.add_parser(command,
                        help=help,
                        add_help=False,
                        description=desc)

                subparser.add_argument('-h', '--help',
                    action='help',
                    help=argparse.SUPPRESS,
                )

                self.subcommands[command] = subparser
                for (args, kwargs) in arguments:
                    subparser.add_argument(*args, **kwargs)
                subparser.set_defaults(func=callback)

    def main(self, argv):
        """Entry point of the command shell."""
        defaults = {}
        # First read out file based configuration
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser('~/.thirty.cfg'))
        if config.has_section('thirtyloops'):
            defaults = dict(config.items('thirtyloops'))

        parser = self.get_base_parser()

        # set the configfile as defaults
        parser.set_defaults(**defaults)

        subcommand_parser = self.get_subcommand_parsers(parser)
        self.parser = subcommand_parser

        args = subcommand_parser.parse_args(argv)

        # Handle global arguments
        if args.uri:
            env.base_uri = args.uri
        if args.account:
            env.account = args.account
        if args.api:
            env.api_version = args.api

        args.base_url = "%s/%s/%s" % (args.uri, args.api, args.account)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0

        #args.func(self.cs, args)
        args.func(args)

    @utils.arg('command', metavar='<subcommand>', nargs='?',
                    help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            print ascii_art()
            self.parser.print_help()

    ##
    # Helper functions
    ##
    def _format_output(self, obj):
        return json.dumps(obj, indent=4)

    def _format_error(self, error):
        return json.dumps(error, indent=4)

    def _poll_logbook(self, uuid):
        import time

        lbh = LogBookHandler(uuid)
        time.sleep(3)
        while True:
            messages = lbh.fetch()
            for msg in messages:
                if msg['loglevel'] == 1:
                    sys.stdout.write(utils.format_logbook_message(msg))
                    sys.stdout.write('\n')
                elif msg['loglevel'] == 3:
                    sys.stderr.write(utils.format_logbook_message(msg))
                    sys.stderr.write('\n')
            if lbh.status in 'finished':
                sys.stdout.write('\n')
                break
            if lbh.status in 'error':
                sys.stderr.write('\n')
                break
            time.sleep(5)

def main():
    try:
        ThirtyCommandShell().main(sys.argv[1:])
    except Exception, e:
        print >> sys.stderr, e
        sys.exit(1)
