# webmoney-api
Webmoney api is a python wrapper for webmoney api. It allows you make requests to api, use Keeper Light certificates.

Installation:
```
pip install webmoney-api
```

It gives you output in format:
```
{
    retval:, 
    retdesc:, 
    response:
}
```
response is xml, which was parsed with xmltodict package.

Examples:

```python
>>> api = ApiInterface(WMLightAuthInterface("/home/stas/wmcerts/crt.pem", "/home/stas/wmcerts/key.pem"))
>>> api.x8(purse="R328079907035", reqn=int(time.time()))["response"]
OrderedDict([(u'wmid', OrderedDict([(u'@available', u'0'), (u'@themselfcorrstate', u'0'), (u'@newattst', u'110'), ('#text', u'407414370132')])), (u'purse', OrderedDict([(u'@merchant_active_mode', u'-1'), (u'@merchant_allow_cashier', u'-1'), ('#text', u'R328079907035')]))])
>>> api.x8(purse="R328079907035", reqn=int(time.time()))["response"]["wmid"]["#text"]
u'407414370132'
>>> api.x4(purse="R328079907035", datestart="20100101 00:00:00", datefinish="20140501 00:00:00", reqn=int(time.time())) 
{'response': OrderedDict([(u'@cnt', u'0'), (u'@cntA', u'0')]),
 'retdesc': None,
 'retval': u'0'}
 >>> for order in api.x10(wmid="407414370132", datestart="20100101 00:00:00", datefinish="20140501 00:00:00", reqn=int(time.time()))["response"]["ininvoice"]:
>>>     print order["orderid"], order["amount"], order["state"]
4640849 122.40 2
24 1.00 2
27 0.40 2
```

