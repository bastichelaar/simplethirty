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
"""Utility functions for the thirty command line tool."""
import sys
import json


# Decorator for cli-args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def occurence(string):
    if string.lower() in 'all':
        occurence = 'all'
    else:
        try:
            occurence = int(string)
        except ValueError:
            sys.stderr.write('Occurence needs to be either a number or all.')
            sys.exit(1)

    return occurence


def format_logbook_message(msg):
    attr = []
    if msg['loglevel'] == 1:
        attr.append('34')
        # normal message
        if sys.stdout.isatty:
            formatted_message = '\x1b[%sm%s\x1b[0m' % (
                ';'.join(attr),
                msg['message'])
        else:
            formatted_message = "Info (%s): %s" % (
                msg['asctime'], msg['message'])
    if msg['loglevel'] == 3:
        attr.append('31')
        # we catch an error
        if sys.stderr.isatty:
            formatted_message = '\x1b[%sm%s\x1b[0m' % (
                    ';'.join(attr),
                    msg['message'])
        else:
            formatted_message = "Error (%s): %s" % (
                msg['asctime'], msg['message'])

    return formatted_message


class OutputFormater(object):
    GRAY = '30'
    GREEN = '32'
    YELLOW = '33'
    BLUE = '34'
    WHITE = '37'
    RED = '38'

    def info(self, msg):
        msg = self._format_info(msg)
        sys.stdout.write(msg)
        sys.stdout.flush()

    def error(self, msg):
        msg = self._format_error(msg)
        sys.stderr.write(msg)
        sys.stderr.flush()

    def debug(self, msg):
        msg = self._format_debug(msg)
        sys.stdout.write(msg)
        sys.stdout.flush()


class ResourceOutputFormater(OutputFormater):
    def _format_info(self, msg):
        return json.dumps(msg, indent=4)

    def _format_error(self, msg):
        return self._format_info(msg)

    def _format_debug(self, msg):
        return self._format_info(msg)


class RawOutputFormater(OutputFormater):
    def _format_info(self, msg):
        return json.dumps(msg)

    def _format_error(self, msg):
        return self._format_info(msg)

    def _format_debug(self, msg):
        return self._format_info(msg)
