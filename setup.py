#!/usr/bin/env python
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def run_setup():
    setup(
        name='circus-logstash',
        version='0.0.5',
        description='A Logstash shipper for Circus',
        keywords = 'logstash circus',
        url='https://github.com/seatgeek/circus-logstash',
        author='Philip Cristiano',
        author_email='phil@seatgeek.com',
        license='BSD',
        packages=['circus_logstash'],
        install_requires=[
            'redis',
        ],
        test_suite='tests',
        long_description=read('README.md'),
        zip_safe=True,
        classifiers=[
        ],
        entry_points="""
        [console_scripts]
        """,
    )

if __name__ == '__main__':
    run_setup()
