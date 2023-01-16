import argparse
import configparser
import csv
import os
import sys

from invtranlist import config_to_args

DEFAULT_CONFIG_SECTION = "read_fidelity_csv"

DEFAULT_CONFIG_FILENAME = os.environ.get(
    "INVTRANLIST_CONFIG", default="invtranlist.ini"
)


class FidelityMapper:
    def __init__(self, filename):
        self.filename = filename
        self.parse(self.filename)
        self.rows = []

    def parse(self, filename):
        rows_dict = []
        with open(filename, mode="r") as file:
            dict_reader = csv.DictReader(file)
            self.rows = list(dict_reader)

    def get_type(self, symbol):
        for row in self.rows:
            if symbol in row["symbol"]:
                return row["type"]

        return "FUND"


class FidelityCsv:
    def __init__(self, filename, mapper, header_lineno=6):
        self.filename = filename
        self.mapper = mapper
        self.header_lineno = header_lineno
        [headers, rows_dict] = self.parse_fidelity_history_for_account()
        self.headers = headers
        self.rows = rows_dict

    def get_action(self, row):
        value = row["Action"]
        description = row["Security Description"]
        security = row["Security Type"]
        type = self.mapper.get_type(security)

        if "BOUGHT" in value:
            if type in "FUND":
                return "BUYFUND"
            else:
                return "BUYSTOCK"

        if "REINVESTMENT" in value:
            return "REINVEST"

        if "DIVIDEND" in value:
            return "INCOME"

        if "LONG-TERM CAP GAIN" in value:
            return "INCOME"

        if "SHORT-TERM CAP GAIN" in value:
            return "INCOME"

        return "NONE"

    def parse_fidelity_history_for_account(self):
        rows_dict = []
        with open(self.filename, mode="r") as file:
            csvreader = csv.reader(file)
            lines = 0
            # header_lineno = 6
            headers = []
            ended = False
            for row in csvreader:
                lines += 1
                if lines < self.header_lineno:
                    continue
                if lines == self.header_lineno:
                    headers = row
                else:
                    if len(row) == 0:
                        ended = True

                    if not ended:
                        cols = min(len(headers), len(row))
                        # print(cols)
                        row_dict = {}
                        for i in range(0, cols):
                            key = headers[i]
                            value = row[i]
                            # print(key, value)
                            row_dict[key] = value
                        rows_dict.append(row_dict)
        return [headers, rows_dict]


def main(args):
    fidelity_mapper = FidelityMapper(args.mapper)
    fidelity_csv = FidelityCsv(args.input, fidelity_mapper, args.header_lineno)

    write_output_file(fidelity_csv, args.output)


def write_output_file(fidelity_csv, filename):
    # txn_type,trade_date,symbol,units,unitprice,total,memo
    headers = [
        "txn_type",
        "trade_date",
        "symbol",
        "units",
        "unitprice",
        "total",
        "memo",
    ]

    print("# Writing to filename=%s" % (filename))

    with open(filename, "w") as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the headers
        csvwriter.writerow(headers)

        for row in fidelity_csv.rows:
            txn_type = fidelity_csv.get_action(row)
            # Run Date, 01/03/2023
            trade_date = row["Run Date"]
            symbol = row["Symbol"]
            units = row["Quantity"]
            unitprice = row["Price ($)"]
            total = row["Amount ($)"]
            memo = row["Action"]
            new_row = [txn_type, trade_date, symbol, units, unitprice, total, memo]
            csvwriter.writerow(new_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True, help="Input file")
    parser.add_argument("--output", "-o", required=True, help="Output file")
    parser.add_argument("--mapper", "-m", required=True, help="Mapper file")
    parser.add_argument(
        "--header_lineno",
        "-l",
        type=int,
        required=True,
        help="Line number of the header row",
    )
    config = configparser.ConfigParser()
    config_filename = DEFAULT_CONFIG_FILENAME
    if os.access(config_filename, os.R_OK):
        print("# Reading config file=%s" % config_filename)
        config.read(config_filename)
        config_args = config_to_args(config, DEFAULT_CONFIG_SECTION)
        print("# sys.argv=%s" % sys.argv[1:])
        config_args = config_args + sys.argv[1:]
        print("# config_args=%s" % config_args)
        args = parser.parse_args(args=config_args)
    else:
        print("# sys.argv=%s" % sys.argv)
        args = parser.parse_args()

    main(args)
