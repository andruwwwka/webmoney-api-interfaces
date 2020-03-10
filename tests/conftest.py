import pytest
import mock
import os

from webmoney_api_interfaces import ApiInterface
from webmoney_api_interfaces import WMLightAuthInterface


@pytest.fixture(scope='session')
@mock.patch('os.path.exists')
def api(mock_os_exists):
    certificate_path = os.getenv('WM_CERTPATH')
    key_path = os.getenv('WM_KEYPATH')
    auth_interface = WMLightAuthInterface(certificate_path, key_path)
    api_interface = ApiInterface(auth_interface)
    return api_interface
