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


import re
import requests
import requests_mock
import unittest

from ..producer import WebsiteCheck


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


if __name__ == '__main__':
    unittest.main()
