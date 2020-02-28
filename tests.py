"""
For running tests you should specify 2 envvars:


"""
import os
from pprint import pprint

import pytest
import time

from webmoney_api_interfaces import ApiInterface
from webmoney_api_interfaces import WMLightAuthInterface


@pytest.fixture(scope="session")
def api():
    return ApiInterface(WMLightAuthInterface(
        os.getenv("WM_CERTPATH"), os.getenv("WM_KEYPATH")
    ))

def test_x4(api):
    # assert isinstance(api, ApiInterface)
    assert dict(
        api.x4(purse="R328079907035", datestart="20100101 00:00:00", datefinish="20140501 00:00:00", reqn=int(time.time()))["response"]
    ) == {u'@cnt': u'0', u'@cntA': u'0'}

def test_x8(api):
    assert dict(
        api.x8(purse="R328079907035", reqn=int(time.time()))["response"]["wmid"]
    ) == {'#text': u'407414370132',
         u'@available': u'0',
         u'@newattst': u'110',
         u'@pasdoc': u'1',
         u'@themselfcorrstate': u'0'}