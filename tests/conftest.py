import os
import pytest

from webmoney_api_interfaces import ApiInterface
from webmoney_api_interfaces import WMLightAuthInterface


@pytest.fixture(scope='session')
def api():
    certificate_path = os.getenv('WM_CERTPATH')
    key_path = os.getenv('WM_KEYPATH')
    auth_interface = WMLightAuthInterface(certificate_path, key_path)
    api_interface = ApiInterface(auth_interface)
    return api_interface
