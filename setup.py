#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='stardate',
    version='0.1',
    description='A daily reminder for a log entry, promptly forwarded to posterous.',
    author='Scott Robinson',
    author_email='scott@quadhome.com',

    packages=find_packages(exclude='tests'),
    package_data={
        'stardate': [
            'data/*.txt',
            'templates/*.msg',
        ],
    },

    install_requires=[
        'lamson',
        'apscheduler',
    ],

    tests_require=['nose'],
    test_suite='nose.collector',
)
