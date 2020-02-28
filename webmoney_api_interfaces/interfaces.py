#-*- coding: utf-8 -*-
import logging

from lxml import etree
import requests as r
from pprint import pprint, pformat
import uuid
import xmltodict
import os

import ssl

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.exceptions import SSLError
from wmsigner import Signer


class Ssl3HttpAdapter(HTTPAdapter):

    """Transport adapter" that allows us to use SSLv3."""

    def init_poolmanager(self, connections, maxsize, block=False):

        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_SSLv23)


class AuthInterface(object):

    """
    Интерфейс аунтефикации
    """

    def wrap_request(self, request_params):
        """

        """
        return request_params

    def wrap_body_tree(self, tree):
        """

        """
        return tree

    def get_url_by_name(self, name):
        raise NotImplemented


class WMLightAuthInterface(AuthInterface):

    def __init__(self, pub_cert, priv_key=None):
        if not os.path.exists(pub_cert):
            raise ValueError("Incorrect path to pub certificate")
        if priv_key and not os.path.exists(priv_key):
            raise ValueError("Incorrect path to private key")

        self.cert = os.path.abspath(
            pub_cert) if priv_key is None else (os.path.abspath(pub_cert),
                                                os.path.abspath(priv_key))

    def wrap_request(self, request_params):
        request_params.update({"cert": self.cert})
        return request_params

    def get_url_by_name(self, name):
        if name == "FindWMPurseNew":
            return "https://w3s.wmtransfer.com/asp/XMLFindWMPurseCertNew.asp"
        return "https://w3s.wmtransfer.com/asp/XML{}Cert.asp".format(name)


class WMProAuthInterface(AuthInterface):
    SIGN_STRUCTURE = {"testwmpurse": ("wmid", "purse"),
                      "getpurses": ("wmid", "reqn"),
                      "invoice": ("orderid", "customerwmid", "storepurse", "amount", "desc",
                                  "address", "period", "expiration", "reqn"),
                      "trans": ("reqn", "tranid", "pursesrc", "pursedest", "amount",
                                "period", "pcode", "desc", "wminvid"),
                      "getoperations": ("purse", "reqn"),
                      "getoutinvoices": ("purse", "reqn"),
                      "finishprotect": ("wmtranid", "pcode", "reqn"),
                      "message": ("receiverwmid", "reqn", "msgtext"),
                      "testsign": ("wmid", "wmid", "plan", "sign"),
                      "getininvoices": ("wmid", "wminvid",
                                        "datestart", "datefinish", "reqn")}

    def __init__(self, wmid, password, keys_file_path):
        self.wmid = wmid
        self.signer = Signer(wmid=wmid, keys=keys_file_path, password=password)

    def _get_sing(self, tree):
        interface_name = tree.findall('.//')[1].tag
        interface_tag = tree.find(interface_name)

        sign_params_names = self.SIGN_STRUCTURE[interface_name]
        return self.signer.sign(''.join([tree.find(param).text
                                         if tree.find(param) is not None else interface_tag.find(param).text
                                         for param in sign_params_names]))

    def wrap_body_tree(self, tree):
        wmid = etree.Element('wmid')
        wmid.text = self.wmid
        tree.append(wmid)

        sign = etree.Element('sign')
        sign.text = self._get_sing(tree)
        tree.append(sign)

        return tree

    def get_url_by_name(self, name):
        if name == "FindWMPurseNew":
            return "https://w3s.webmoney.ru/asp/XMLFindWMPurseNew.asp"
        return "https://w3s.webmoney.ru/asp/XML{}.asp".format(name)


class ApiInterface(object):

    """
    Основной интерфейс API.
    Пример использования::

        api = ApiInterface(WMLightAuthInterface(
                    "/home/stas/wmcerts/crt.pem", "/home/stas/wmcerts/key.pem"))

        import time
        api.x8(purse="R328079907035", reqn=int(time.time()))[
            "response"]["wmid"]["#text"]

    Проксирует интерфейсы X1 - X10 в соответствующие атрибуты.
    """

    API_METADATA = {"FindWMPurseNew": {"root_name": "testwmpurse",
                                       "aliases": ["x8"]},
                    "Purses": {"root_name": "getpurses",
                               "aliases": ["x9"],
                               "response_name": "purses"},
                    "Invoice": {"root_name": "invoice",
                                "aliases": ["x1"]},
                    "Trans": {"root_name": "trans",
                              "aliases": ["x2"],
                              "response_name": "operation"},
                    "Operations": {"root_name": "getoperations",
                                   "aliases": ["x3"],
                                   "response_name": "operations"},
                    "OutInvoices": {"root_name": "getoutinvoices",
                                    "aliases": ["x4"],
                                    "response_name": "outinvoices"},
                    "FinishProtect": {"root_name": "finishprotect",
                                      "aliases": ["x5"],
                                      "response_name": "operation"},
                    "SendMsg": {"root_name": "message",
                                "aliases": ["x6"]},
                    "ClassicAuth": {"root_name": "testsign",
                                    "aliases": ["x7"]},
                    "InInvoices": {"root_name": "getininvoices",
                                   "aliases": ["x10"],
                                   "response_name": "ininvoices"}}
    """
    Метаданные интерфейсов API Webmoney.
    Имеют следующую структуру::

    	{<interface_name>:{
    		"root_name": <root_name>, 
    		"aliases": [<string>, <string>, ...], 
    		"response_name": <response_name>
    	}}

    Параметры имеют следующий смысл:

    :param interface_name: Название интерфейса в URL, например, для X9 (https://w3s.webmoney.ru/asp/XMLPurses.asp) названием будет Purses. Название используется при конструировании урла 
    :param root_name: название рутового элемента секции данных запроса 
    :param response_name: Название рутового элемента секции данных ответа(если не задан, берется **root_name**)

    """

    def __init__(self, authenticationStrategy):
        self.authStrategy = authenticationStrategy

    def _check_params(self, params):
        for key, value in params:
            assert key in self.API_METADATA

    def _get_root_name_by_interface_name(self, interface_name):
        assert interface_name in self.API_METADATA, "Incorrect interface name: %s" % interface_name
        return self.API_METADATA[interface_name]["root_name"]

    def _create_xml_request_params(self, interface_name, params):
        """
        Создает подзапрос, различающийся для каждого WM интерфейса
        :param interface_name: Название интерфейса
        :param params: Словарь аргументов
        """
        root_name = self._get_root_name_by_interface_name(interface_name)
        tree = etree.Element(root_name)
        for key, value in params.items():
            subelement = etree.Element(key)
            subelement.text = value
            tree.append(subelement)

        return tree

    def _create_request(self, interface, **kwargs):
        """
        Создает словарь параметров запроса к api. Тут вызывается функция :func:`AuthInterface.wrap_request`
        """
        request_params = {
            "url": self.authStrategy.get_url_by_name(interface), "verify": False}

        request_params = self.authStrategy.wrap_request(request_params)

        return request_params

    def _create_body(self, interface, **params):
        """
        Создает XML-тело запроса. Тут вызывается функция :func:`AuthInterface.wrap_body_tree`
        """
        tree = etree.Element("w3s.request")

        reqn = params.pop("reqn", None)
        _ = etree.Element("reqn")

        if reqn:
            _.text = str(int(reqn))
        else:
            _.text = ""

        tree.append(_)

        tree.append(self._create_xml_request_params(interface, params))

        tree = self.authStrategy.wrap_body_tree(tree)

        return etree.tostring(tree)

    def _make_request(self, interface, **params):
        """
        Функция, делающая HTTP запрос к API
        """
        request_params = self._create_request(interface, **params)
        body = self._create_body(interface, **params)

        request_params.update({"data": body})

        # SSL v3 compability
        # see http://docs.python-requests.org/en/latest/user/advanced/
        s = r.Session()
        a = Ssl3HttpAdapter(max_retries=3)
        s.mount('https://', a)

        response = s.get(**request_params)

        if response.status_code != 200:
            raise ValueError("Bad response from webmoney api server: ({}) {}".format(response.status_code, response.text))

        out = xmltodict.parse(response.text)["w3s.response"]
        # print out
        # pprint(request_params)
        # print self.API_METADATA[interface]["root_name"]

        try:
            response_name = self.API_METADATA[interface].get(
                "response_name", None) or self.API_METADATA[interface]["root_name"]
            resp = out[response_name]
        except:
            out = u"Error while requesting API. retval = %s, retdesc = %s" % (
                out["retval"], out["retdesc"]) + "\n" +\
                u"Request data: %s" % pformat(request_params)
            raise ValueError(out.encode("utf-8"))

        return {"retval": out["retval"],
                "retdesc": out["retdesc"],
                "response": resp}

    def __getattribute__(self, name):
        if name in ApiInterface.API_METADATA.keys():
            def _callback(**params):
                return self._make_request(name, **params)

            return _callback

        for key, aliases in ApiInterface.API_METADATA.items():
            aliases = aliases["aliases"]
            if name.lower() in aliases:
                def _callback(**params):
                    return self._make_request(key, **params)
                return _callback

        return object.__getattribute__(self, name)
