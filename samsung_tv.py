#!/usr/bin/env python

"""
usage: samsung_tv.py [-h] [--port serialport]

samsung_tv.py --port /dev/ttyS0 cmd [args]
"""

import argparse
import logging
import os
import sys

import exlink

class ListCommandsAction(argparse.Action):
    """Show a list of available commands and exists"""
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(ListCommandsAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def _show_commands(self):
        methods = exlink.TVRemote.method_list()
        commands = exlink.TVRemote.command_list()
        out = []
        for cmd in commands:
            method = exlink.TVRemote.__dict__["cmd_"+cmd]
            out.append("%s - %s" % (cmd, method.__doc__))
        print("\n".join(out))

    def __call__(self, parser, namespace, values, option_string=None):
        self._show_commands()
        parser.exit()

class SamsungCLI(object):
    def __init__(self):
        self._port = None
        self._tv = None
        self._errors = []
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger("")

        self._args = self._init_parser()

    def _init_parser(self):
        parser = argparse.ArgumentParser(
            description='Send commands to a Samsung TV using a serial port.')

        parser.add_argument(
            '-l', '--list', action=ListCommandsAction, default=False,
            help='List of available commands')

        parser.add_argument(
            '-p', '--port', metavar='serialport', type=str, default='/dev/ttyUSB0',
            help='Serial port connected to a Samsung TV via ex-link cable (/dev/ttyS0 by default)')

        parser.add_argument(
            'command', metavar='command', type=str,
            help='Command to send to TV')

        parser.add_argument(
            'args', metavar='args', type=str, nargs='*',
            help='Arguments for the command')

        return parser.parse_args()


    def _check_serialport_exists(self):
        """Check if the user provided serial port exists"""
        try:
            st = os.stat(self._args.port)
            return True
        except OSError:
            self._errors.append("Device '%s' is not accessible or does no exist" % (self._args.port,))
            return False

    def _check_command_exists(self):
        if not self._args.command in exlink.TVRemote.command_list():
            self._errors.append("'%s' is not a valid command. Try -l to get a list of valid commands" % (self._args.command,))
            return False
        return True

    def _check_command_arguments(self):
        """Check if the user has provided the correct number of argumets"""
        cmd = self._args.command
        args = self._args.args

        if cmd == 'volume_set' or cmd == 'tv_channel_set':
            if len(args) != 1:
                self._errors.append("%s requires one argument" % (cmd,))
                return False

            try:
                n = int(args[0])
                if n < 0 or n > 255:
                    self._errors.append("argument should be a number between 0 and 255")
                    return False
            except ValueError:
                self._errors.append("argument is not a valid number between 0 and 255")
                return False
        else:
            if len(args) != 0:
                self._errors.append("%s does not need arguments" % (cmd,))
                return False

        return True

    def _check_args(self):
        """several checks on command line arguments"""
        tests = [
            self._check_serialport_exists,
            self._check_command_exists,
            self._check_command_arguments,
        ]
        result = True
        for testfunc in tests:
            result = result and testfunc()
            if not result:
                return False

        return result

    def show_errors(self):
        """logs all the errors to default logger"""
        self._logger.error("\n".join(self._errors))

    def run(self):
        if not self._check_args():
            self.show_errors()
            sys.exit(1)

        self._tv = exlink.TVRemote(self._args.port)
        command_method = getattr(self._tv, "cmd_" + self._args.command)
        command_method(*[int(a) for a in self._args.args])

if __name__ == '__main__':
    cli = SamsungCLI()
    cli.run()
