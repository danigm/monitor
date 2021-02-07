#!/usr/bin/env python3

# Copyright (C) 2021 Daniel Garcia <dani@danigm.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import argparse
import datetime
import re
import requests
import sys
import time


class Config:
    timeout = 5


class WebsiteCheck:

    def __init__(self, url, regex=None):
        '''
        :param url: The url to check.
        :param regex: A raw string containing the regular expression to check
        or a re.Pattern object.
        '''

        self.url = url
        self.request_time = None

        if isinstance(regex, re.Pattern):
            self.regex = regex
        elif regex:
            self.regex = re.compile(regex)
        else:
            self.regex = None

        self.time = 0
        self.code = 500
        self.response = None
        self.valid = False

    def request(self):
        '''
        Tries the request to the url and stores the result in the response
        param. The response is also returned if there's no exceptions.

        This uses the python requests library to do the request and can raise
        the same exceptions.
        '''

        self.request_time = datetime.datetime.now()
        self.response = requests.get(self.url, timeout=Config.timeout)
        self.time = self.response.elapsed
        self.code = self.response.status_code
        self.valid = True

        # if we've the regex the valid status is set to true just if the
        # regular expression matches the content
        if self.regex:
            self.valid = bool(self.regex.search(self.response.text))

        return self.response


def do_request(websites):
    '''
    Do the request for each websites

    :param websites: The websites to check, it should be an iterable of
    :class:`WebsiteCheck <WebsiteCheck>`

    Returns: True if all requests are done correctly, otherwise returns False.
    '''

    all_ok = True

    for check in websites:
        try:
            check.request()
        except requests.exceptions.RequestException as e:
            # The error in red in error output
            print(f'\033[1;31m{e}\033[0;0m', file=sys.stderr)
            all_ok = False
        else:
            date = datetime.datetime.now().ctime()
            info = f'[{date}]: Request {check.code} -> {check.valid} {check.url}'
            print(f'\033[1;34m{info}\033[0;0m', file=sys.stdout)

    return all_ok


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor a website.')

    parser.add_argument(
        'url', nargs='+',
        help='The websites to monitor. Use the full url, '
        'for example http://github.com')

    parser.add_argument(
        '-m', '--monitor', type=int, default=0,
        help='Run this as daemon, making the check every MONITOR seconds')

    parser.add_argument(
        '-r', '--regex', type=str, default='',
        help='Regular expression to check if it is in the page contents')

    parser.add_argument(
        '-t', '--timeout', type=float, default=5.0,
        help='Connection timeout in seconds. You can use float point here, '
        'for example 0.005 for 5 milisecond')

    args = parser.parse_args()

    if args.timeout:
        Config.timeout = args.timeout

    websites = [WebsiteCheck(u, regex=args.regex) for u in args.url]

    # no monitor, just one time
    if not args.monitor:
        response = do_request(websites)
        sys.exit(0 if response else 1)

    # Periodic check every args.monitor seconds
    try:
        while True:
            do_request(websites)
            time.sleep(args.monitor)
    except KeyboardInterrupt:
        sys.exit(0)
