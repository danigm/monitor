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
import random


def callback(*args):
    pass


class Future:
    def __init__(self, mock, fail=False):
        self.mock = mock
        self.errback = callback
        self.callback = callback

        self.fail = fail

    def add_errback(self, callback):
        self.errback = callback
        return self

    def add_callback(self, callback):
        self.callback = callback
        return self


class MockProducer:
    def __init__(self,
                 fail=False,
                 bootstrap_servers=None,
                 ssl_certfile='',
                 ssl_keyfile='',
                 ssl_cafile='',
                 security_protocol='SSL',
                 value_serializer=lambda m: m):

        self.bootstrap_servers = bootstrap_servers
        self.ssl_certfile = ssl_certfile
        self.ssl_keyfile = ssl_keyfile
        self.ssl_cafile = ssl_cafile
        self.security_protocol = security_protocol
        self.value_serializer = value_serializer

        self.fail = fail
        self.future = None
        self.data = None
        self.serialized = None

    def send(self, topic, data):
        self.data = data
        self.serialized = self.value_serializer(self.data)
        self.future = Future(self)
        return self.future

    def flush(self):
        if not self.future:
            return

        if self.fail:
            self.future.errback(Exception('Forced fail'))
        else:
            self.future.callback(self.data)


class ConsumerData:
    def __init__(self):
        self.value = {
            'time': random.randint(100, 10*1000*1000),
            'code': random.choice([200, 404, 302]),
            'request_time': datetime.datetime.now().isoformat(),
            'valid': random.choice([True, False]),
            'regex': '',
            'url': f'http://test{random.randint(0, 10)}.com',
        }


class MockConsumer:
    def __init__(self,
                 topic,
                 elements=100,
                 bootstrap_servers=None,
                 ssl_certfile='',
                 ssl_keyfile='',
                 ssl_cafile='',
                 security_protocol='SSL',
                 value_serializer=lambda m: m):

        self.bootstrap_servers = bootstrap_servers
        self.ssl_certfile = ssl_certfile
        self.ssl_keyfile = ssl_keyfile
        self.ssl_cafile = ssl_cafile
        self.security_protocol = security_protocol
        self.value_serializer = value_serializer

        self.data = self._gen_fake_data(elements)

    def __iter__(self):
        return iter(self.data)

    def _gen_fake_data(self, elements):
        data = []
        for i in range(elements):
            website = ConsumerData()
            data.append(website)

        return data
