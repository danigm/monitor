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
        self.response = requests.get(self.url)
        self.time = self.response.elapsed
        self.code = self.response.status_code
        self.valid = True

        # if we've the regex the valid status is set to true just if the
        # regular expression matches the content
        if self.regex:
            self.valid = bool(self.regex.search(self.response.text))

        return self.response


def do_request(check):
    try:
        info = f'[{datetime.datetime.now().ctime()}]: Request {check.url}'
        print(f'\033[1;34m{info}\033[0;0m', file=sys.stdout)
        check.request()
    except requests.exceptions.RequestException as e:
        # The error in red in error output
        print(f'\033[1;31m{e}\033[0;0m', file=sys.stderr)
        return False

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor a website.')

    parser.add_argument(
        'url',
        help='The website to monitor. Use the full url, '
        'for example http://github.com')

    parser.add_argument(
        '-m', '--monitor', type=int, default=0,
        help='Run this as daemon, making the check every MONITOR seconds')

    args = parser.parse_args()

    check = WebsiteCheck(args.url)

    # no monitor, just one time
    if not args.monitor:
        response = do_request(check)
        sys.exit(0 if response else 1)

    # Periodic check every args.monitor seconds
    try:
        while True:
            do_request(check)
            time.sleep(args.monitor)
    except KeyboardInterrupt:
        sys.exit(0)
