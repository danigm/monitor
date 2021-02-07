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


import datetime
import re
import requests


class WebsiteCheck:

    def __init__(self, url, regex=None):
        '''
        :param url: The url to check.
        :param regex: A raw string containing the regular expression to check.
        '''

        self.url = url
        self.datetime = datetime.datetime.now()
        self.regex = re.compile(regex) if regex else None
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

        self.response = requests.get(self.url)
        self.time = self.response.elapsed
        self.code = self.response.status_code
        self.valid = True

        # if we've the regex the valid status is set to true just if the
        # regular expression matches the content
        if self.regex:
            self.valid = self.regex.match(self.response.text)

        return self.response
