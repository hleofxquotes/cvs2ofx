import json
import os

import xmltodict

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

filename = os.path.join(
    THIS_DIR, os.pardir, "private/FIDELITY20230125131402309731-pretty.xml"
)


def get_transactions(ofx):
    # INVSTMTMSGSRSV1.INVSTMTTRNRS.INVSTMTRS.INVTRANLIST.BUYMF(s)
    # ...BUYSTOCK(s)
    # ...INCOME(s)
    transactions = ofx["INVSTMTMSGSRSV1"]["INVSTMTTRNRS"]["INVSTMTRS"]["INVTRANLIST"]
    return transactions


def get_buymf(transactions):
    buymf = transactions["BUYMF"]
    if not hasattr(buymf, "__len__"):
        a_list = [buymf]
        buymf = a_list

    return buymf


with open(filename) as xml_file:
    data_dict = xmltodict.parse(xml_file.read())
    ofx = data_dict["OFX"]
    # print(ofx)

    signon = ofx["SIGNONMSGSRSV1"]
    invst = ofx["INVSTMTMSGSRSV1"]
    seclist = ofx["SECLISTMSGSRSV1"]

    transactions = get_transactions(ofx)
    json_data = json.dumps(transactions, indent=2)
    print(json_data)
