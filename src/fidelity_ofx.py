import argparse
import json
import re
import xml.dom.minidom
from io import StringIO

import xmltodict


def cleanup(filename):
    with open(filename) as f:
        ofx_string = f.read()
    closing_tags = [
        t.upper() for t in re.findall(r"(?i)</([a-z0-9_\.]+)>", ofx_string)
    ]
    # for closing_tag in closing_tags:
    #     print(closing_tag)
    tags = 0
    header = StringIO()
    xml_body = StringIO()
    tokens = re.split(r"(?i)(</?[a-z0-9_\.]+>)", ofx_string)
    last_open_tag = None
    for token in tokens:
        # print(token)
        is_closing_tag = token.startswith("</")
        is_processing_tag = token.startswith("<?")
        is_cdata = token.startswith("<!")
        is_tag = token.startswith("<") and not is_cdata
        is_open_tag = is_tag and not is_closing_tag and not is_processing_tag
        if is_tag:
            tags = tags + 1
            if last_open_tag is not None:
                if tags > 0:
                    xml_body.write("</%s>" % last_open_tag)
                else:
                    header.write("</%s>" % last_open_tag)
                # print("</%s>" % last_open_tag, end="")
                last_open_tag = None
        if is_open_tag:
            tag_name = re.findall(r"(?i)<([a-z0-9_\.]+)>", token)[0]
            if tag_name.upper() not in closing_tags:
                last_open_tag = tag_name

        if tags > 0:
            xml_body.write(token)
        else:
            header.write(token)
            # print(token, end="")

    return [header, xml_body]


class FidelityOfx:
    def __init__(self, filename):
        [header, xml_body] = cleanup(filename)
        xml_body.seek(0)
        self.xml_string = xml_body.read()
        self.dict = xmltodict.parse(self.xml_string)

    def to_xml_str(self):
        return xml.dom.minidom.parseString(self.xml_string).toprettyxml()

    def to_json_str(self):
        return json.dumps(self.dict, indent=4)

    def to_csv(self):
        return ""

    # 13.9.2.2 Investment Statement Response <INVSTMTRS>
    def get_investment_statement_response(self):
        response = self.dict.get("OFX", {}).get("INVSTMTMSGSRSV1", {}).get("INVSTMTTRNRS", {}).get("INVSTMTRS",
                                                                                                   {})
        return response

    # return a list of transactions
    def get_transactions(self):
        # INVSTMTMSGSRSV1.INVSTMTTRNRS.INVSTMTRS.INVTRANLIST.BUYMF(s)
        # ...BUYSTOCK(s)
        # ...INCOME(s)
        transactions = self.get_investment_statement_response().get(
            "INVTRANLIST", {})
        return transactions

    def get_positions(self):
        # OFX.INVSTMTMSGSRSV1.INVSTMTTRNRS.INVSTMTRS.INVPOSLIST
        positions = self.get_investment_statement_response().get(
            "INVPOSLIST", {})
        return positions

    def get_securities(self):
        # OFX.SECLISTMSGSRSV1.SECLIST
        securities = self.dict.get("OFX", {}).get("SECLISTMSGSRSV1", {}).get(
            "SECLIST", {})
        return securities

    def get_aggregate_as_list(self, dict, name):
        aggregate = dict.get(name, {})
        if not hasattr(aggregate, "__len__"):
            a_list = [aggregate]
            aggregate = a_list

        return aggregate

    # Buy mutual fund
    def get_buymf(self, transactions):
        return self.get_aggregate_as_list(transactions, "BUYMF")

    def get_sellmf(self, transactions):
        return self.get_aggregate_as_list(transactions, "SELLMF")

    def get_buystock(self, transactions):
        return self.get_aggregate_as_list(transactions, "BUYSTOCK")

    def get_sellstock(self, transactions):
        return self.get_aggregate_as_list(transactions, "SELLSTOCK")

    def get_income(self, transactions):
        return self.get_aggregate_as_list(transactions, "INCOME")

    def get_posmf(self, positions):
        return self.get_aggregate_as_list(positions, "POSMF")

    # POSSTOCK
    def get_posstock(self, positions):
        return self.get_aggregate_as_list(positions, "POSSTOCK")

    # MFINFO
    def get_mfinfo(self, securities):
        return self.get_aggregate_as_list(securities, "MFINFO")

    # STOCKINFO
    def get_stockinfo(self, securities):
        return self.get_aggregate_as_list(securities, "STOCKINFO")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    fidelity_ofx = FidelityOfx(args.input)

    output = None
    if args.output.endswith(".xml"):
        output = fidelity_ofx.to_xml_str()
    elif args.output.endswith(".json"):
        output = fidelity_ofx.to_json_str()
    elif args.output.endswith(".csv"):
        output = fidelity_ofx.to_csv()
    else:
        output = fidelity_ofx.to_xml_str()

    print(output, file=open(args.output, "w"))
