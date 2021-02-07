#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

import monitor


dist_name = 'websites-monitor'
description = '''
System that monitors website availability over the network, produces metrics
about this and passes these events through an Aiven Kafka instance into an
Aiven PostgreSQL database.
'''


setup(
    name=dist_name,
    description=description,
    version=monitor.__version__,
    author='danigm',
    author_email='dani@danigm.net',
    url='https://github.com/danigm/monitor',
    packages=['monitor'],
    license='GPL3',
    keywords='monitor kafka postgresql',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL3 License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
