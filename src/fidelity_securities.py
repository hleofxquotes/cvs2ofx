import argparse
import csv

from ofxtools import OFXTree

FIELD_NAMES = [
    "uniqueid",
    "uniqueidtype",
    "secname",
    "ticker",
    "unitprice",
    "dtasof",
    "cursym",
]


def create_columns(security):
    columns = {
        "uniqueid": security.uniqueid,
        "uniqueidtype": security.uniqueidtype,
        "secname": security.secname,
        "ticker": security.ticker,
        "unitprice": security.unitprice,
        "dtasof": security.dtasof,
        "cursym": security.cursym,
    }
    return columns


def create_rows(input):
    rows = []
    ofx_tree = OFXTree()
    with open(input, "rb") as f:
        ofx_tree.parse(f)
        ofx = ofx_tree.convert()
        rows = create_rows_from_securities(ofx.securities)
    return rows


def create_rows_from_securities(securities):
    rows = []
    for security in securities:
        columns = create_columns(security)
        rows.append(columns)
    return rows


def write_csv_file(rows, output):
    with open(output, "w") as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    # writing to csv file
    write_csv_file(create_rows(args.input), args.output)
