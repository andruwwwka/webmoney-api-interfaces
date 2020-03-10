#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup, Command

NAME = 'webmoney-api-interfaces'
DESCRIPTION = 'Wrapper for webmoney interfaces (http://wiki.webmoney.ru/projects/webmoney/wiki/xml_interfeysy).'
URL = 'https://github.com/andruwwwka/webmoney-api-interfaces'
EMAIL = 'andruwwwka@gmail.com'
AUTHOR = 'Andrey Leontyev'
REQUIRES_PYTHON = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*'
VERSION = '0.1.0'

REQUIRED = [
    'lxml==4.5.0',
    'requests==2.23.0',
    'wmsigner==0.1.1',
    'xmltodict==0.12.0'
]

TEST_REQUIREMENTS = [
    'pytest>=3',
    'mock>=3.0.5'
]

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", ]),
    install_requires=REQUIRED,
    tests_require=TEST_REQUIREMENTS,
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
