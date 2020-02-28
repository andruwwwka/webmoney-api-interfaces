#!/usr/bin/env python
from pip.req import parse_requirements
from setuptools import setup

setup(name='webmoney-api',
      version='0.0.11',
      description='Wrapper for webmoney interfaces (https://wiki.webmoney.ru/projects/webmoney/wiki/WM-API)',
      author='Stas Kaledin',
      author_email='staskaledin@gmail.com',
      url='https://bitbucket.org/sallyruthstruik/python-webmoney-api',
      packages=['webmoney_api_interfaces'],
      install_requires=[str(ir.req) for ir in parse_requirements("requirements.txt", session=-1)])
