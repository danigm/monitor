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
import psycopg2
import requests_mock
import unittest
from unittest.mock import patch

from .kafkamocks import MockConsumer

from ..consumer import create_table_if_not_exists
from ..consumer import store
from ..consumer import consume

from ..producer import WebsiteCheck


TEST_DB = 'postgres://user:passwd@postgres:5432/db'


class TestDB(unittest.TestCase):

    def setUp(self):
        self.db = psycopg2.connect(TEST_DB)

    def tearDown(self):
        cur = self.db.cursor()
        cur.execute("drop table if exists websites;")
        self.db.commit()
        self.db.close()

    def test_create(self):
        cur = self.db.cursor()
        cur.execute("select exists(select relname from pg_class where relname='websites');")  # noqa: E501
        exists = cur.fetchone()[0]
        self.assertEqual(exists, False)

        create_table_if_not_exists(self.db)

        cur.execute("select exists(select relname from pg_class where relname='websites');")  # noqa: E501
        exists = cur.fetchone()[0]
        self.assertEqual(exists, True)

    @requests_mock.Mocker()
    def test_store(self, m):
        m.get('http://test.com', text='resp', status_code=200)

        create_table_if_not_exists(self.db)

        check = WebsiteCheck('http://test.com')
        check.request()
        store(self.db, check.serialized)

        cur = self.db.cursor()
        cur.execute("select url from websites;")
        urls = cur.fetchone()
        self.assertEqual(urls, ('http://test.com', ))


class TestConsumer(unittest.TestCase):

    def setUp(self):
        self.db = psycopg2.connect(TEST_DB)
        create_table_if_not_exists(self.db)

    def tearDown(self):
        cur = self.db.cursor()
        cur.execute("drop table if exists websites;")
        self.db.commit()
        self.db.close()

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_consume(self, fake_out):
        consumer = MockConsumer('website-check', elements=100)
        consume(self.db, consumer)

        output = fake_out.getvalue().split('\n')
        # 101 because the last \n
        self.assertEqual(len(output), 101)

        cur = self.db.cursor()
        cur.execute("select url, code, time, datetime from websites;")
        urls = cur.fetchall()

        self.assertEqual(len(urls), 100)

        website = consumer.data[0].value
        url, code, time, request_time = urls[0]
        self.assertEqual(url, website['url'])
        self.assertEqual(code, website['code'])
        self.assertEqual(time, website['time'])
        self.assertEqual(request_time.isoformat(), website['request_time'])
