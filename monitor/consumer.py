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
import json
import sys

from kafka import KafkaConsumer

from .config import Config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Consume a kafa topic and stores in postgresql.')

    parser.add_argument(
        '-c', '--config', type=str, default='config.ini',
        help='Configuration file.')

    args = parser.parse_args()

    Config.init(args.config)

    consumer = KafkaConsumer(
        Config.kafka_topic,
        bootstrap_servers=Config.kafka_service,
        ssl_certfile=Config.kafka_cert,
        ssl_keyfile=Config.kafka_key,
        ssl_cafile=Config.kafka_ca,
        security_protocol='SSL',
        value_deserializer=lambda m: json.loads(m.decode('ascii')),
    )

    # Listen to kafka events
    try:
        for msg in consumer:
            data = msg.value
            print(f'\033[1;34m{data}\033[0;0m')

            time = data['time']  # time in microseconds
            code = data['code']
            isoformat = data['request_time']
            request_time = datetime.datetime.fromisoformat(isoformat)
            valid = data['valid']
            regex = data['regex']
            url = data['url']

            # TODO: store this in postgersql db

    except KeyboardInterrupt:
        sys.exit(0)
