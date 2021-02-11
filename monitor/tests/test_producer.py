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


import io
import json
import re
import requests
import requests_mock
import unittest
from unittest.mock import patch

from ..producer import WebsiteCheck
from ..producer import do_request

from .kafkamocks import MockProducer


LOREM = '''
Eum totam reiciendis ea corrupti quibusdam autem nobis. Odio dolore voluptate
ea qui excepturi. Quia qui rerum natus dolor. Nemo consectetur provident quis
eum sit quia earum. Modi aspernatur at incidunt consequatur fuga.

Qui qui et minima ut sed. Id quo tempore consequatur et pariatur repellat ad
quo. Quod aut pariatur saepe veniam et voluptatum vel. Omnis nihil omnis et
explicabo velit. Iste illum repudiandae suscipit laboriosam est.

Sit vitae veniam nesciunt corrupti ratione debitis. Et cumque suscipit incidunt
sunt enim qui. Enim sed sed expedita sunt minima culpa dolorem et. Vel aliquam
quidem enim et et eum beatae. Ipsum quae saepe ipsum error eos in. Eos sit
autem rerum.

Omnis dolorem nihil iste aut laboriosam libero itaque. Similique eius suscipit
voluptatibus omnis. Qui mollitia rerum quos voluptatem tenetur eveniet.

Magni asperiores eum alias rem odio rerum eligendi harum. Quia quaerat tenetur
beatae aut atque ipsa facere sunt. Ea esse fuga ipsam nostrum nisi cumque
eveniet voluptatibus. Culpa at dolor sapiente. Quos et ut earum ut.
'''


class TestWebsiteCheck(unittest.TestCase):

    @requests_mock.Mocker()
    def test_200(self, m):
        m.get('http://test.com', text='resp', status_code=200)
        check = WebsiteCheck('http://test.com')
        check.request()
        self.assertEqual(check.code, 200)
        self.assertEqual(check.response.text, 'resp')
        self.assertEqual(check.valid, True)

    @requests_mock.Mocker()
    def test_404(self, m):
        m.get('http://test.com', status_code=404)
        check = WebsiteCheck('http://test.com')
        check.request()
        self.assertEqual(check.code, 404)
        self.assertEqual(check.valid, True)

    @requests_mock.Mocker()
    def test_timeout(self, m):
        m.get('http://test.com', exc=requests.exceptions.Timeout)
        check = WebsiteCheck('http://test.com')
        with self.assertRaises(requests.exceptions.Timeout):
            check.request()

    @requests_mock.Mocker()
    def test_regex(self, m):
        m.get('http://test.com', text=LOREM)
        check = WebsiteCheck('http://test.com', regex='.*odio rerum.*')
        check.request()
        self.assertEqual(check.code, 200)
        self.assertEqual(check.valid, True)

        check = WebsiteCheck(
            'http://test.com',
            regex=re.compile('(odio|qui) RERUM', re.IGNORECASE)
        )
        check.request()
        self.assertEqual(check.code, 200)
        self.assertEqual(check.valid, True)

    @requests_mock.Mocker()
    def test_no_regex(self, m):
        m.get('http://test.com', text=LOREM)
        check = WebsiteCheck('http://test.com', regex='.*NOT FOUND.*')
        check.request()
        self.assertEqual(check.code, 200)
        self.assertEqual(check.valid, False)


class TestDoRequest(unittest.TestCase):

    @requests_mock.Mocker()
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_onesite(self, m, fake_out, fake_err):
        m.get('http://test.com', text='resp', status_code=200)

        urls = ['http://test.com']
        websites = [WebsiteCheck(u) for u in urls]

        producer = MockProducer(
            value_serializer=lambda m: json.dumps(m).encode('ascii'),
        )

        output = ''
        response = do_request(websites, producer)
        self.assertEqual(response, True)
        output = fake_out.getvalue()

        self.assertTrue('http://test.com' in output)

    @requests_mock.Mocker()
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_multisite(self, m, fake_out, fake_err):
        urls = ['http://test.com', 'https://test2.com']

        for url in urls:
            m.get(url, text='resp', status_code=200)

        websites = [WebsiteCheck(u) for u in urls]

        producer = MockProducer(
            value_serializer=lambda m: json.dumps(m).encode('ascii'),
        )

        output = ''
        response = do_request(websites, producer)
        self.assertEqual(response, True)
        output = fake_out.getvalue()

        self.assertTrue('http://test.com' in output)
        self.assertTrue('https://test2.com' in output)

    @requests_mock.Mocker()
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_multisite_fail(self, m, fake_out, fake_err):
        urls = ['http://test.com', 'https://test2.com']

        m.get(urls[0], text='resp', status_code=200)
        m.get(urls[1], exc=requests.exceptions.Timeout)

        websites = [WebsiteCheck(u) for u in urls]

        producer = MockProducer(
            value_serializer=lambda m: json.dumps(m).encode('ascii'),
        )

        output = ''
        response = do_request(websites, producer)
        self.assertEqual(response, False)
        output = fake_out.getvalue()

        self.assertTrue('http://test.com' in output)
        self.assertTrue('https://test2.com' not in output)

    @requests_mock.Mocker()
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_onesite_kafka_error(self, m, fake_out, fake_err):
        m.get('http://test.com', text='resp', status_code=200)

        urls = ['http://test.com']
        websites = [WebsiteCheck(u) for u in urls]

        producer = MockProducer(
            fail=True,
            value_serializer=lambda m: json.dumps(m).encode('ascii'),
        )

        output = ''
        response = do_request(websites, producer)
        self.assertEqual(response, True)
        output = fake_err.getvalue()

        self.assertTrue('Forced fail' in output)

    @requests_mock.Mocker()
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_onesite_error(self, m, fake_out, fake_err):
        m.get('http://test.com', exc=requests.exceptions.Timeout)

        urls = ['http://test.com']
        websites = [WebsiteCheck(u) for u in urls]

        producer = MockProducer(
            value_serializer=lambda m: json.dumps(m).encode('ascii'),
        )

        response = do_request(websites, producer)
        self.assertEqual(response, False)


if __name__ == '__main__':
    unittest.main()
