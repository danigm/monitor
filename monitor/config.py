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


import configparser


class Config:
    timeout = 5
    kafka_service = 'kafka-14341989-danigm-893f.aivencloud.com:19869'
    kafka_topic = 'website-check'
    kafka_cert = 'service.cert'
    kafka_key = 'service.key'
    kafka_ca = 'ca.pem'

    @classmethod
    def init(cls, filename='config.ini'):
        config = configparser.ConfigParser()
        config.read(filename)

        if 'main' not in config:
            return

        main = config['main']

        for key, value in main.items():
            if key == 'timeout':
                cls.timeout = main.getfloat('timeout')
                continue

            setattr(cls, key, value)
