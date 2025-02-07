import argparse
import json
import pprint
import re
import xml.dom.minidom
from io import StringIO

import xmltodict


def cleanup(filename):
    with open(filename) as f:
        ofx_string = f.read()
    closing_tags = [t.upper() for t in re.findall(r"(?i)</([a-z0-9_\.]+)>", ofx_string)]
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


def prettyprint(xml_string):
    return xml.dom.minidom.parseString(xml_string).toprettyxml()


# Press the green button in the gutter to run the script.
def tojson(xml_string):
    doc = xmltodict.parse(xml_string);
    json_data = json.dumps(doc, indent=4)
    return json_data


def tocsv(xml_string):
    doc = xmltodict.parse(xml_string);
    return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    [header, xml_body] = cleanup(args.input)

    xml_body.seek(0)
    xml_string = xml_body.read()

    output = None
    if args.output.endswith(".xml"):
        output = prettyprint(xml_string)
    elif args.output.endswith(".json"):
        output = tojson(xml_string)
    elif args.output.endswith(".csv"):
        output = tocsv(xml_string)
    else:
        output = prettyprint(xml_string)

    print(output, file=open(args.output, "w"))
