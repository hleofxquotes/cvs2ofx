import argparse
import csv

from ofxtools import OFXTree

FIELD_NAMES = [
    "type",
    "fitid",
    "dttrade",
    "memo",
    "uniqueid",
    "uniqueidtype",
    # "incometype",
    "total",
    "currate",
    "cursym",
    # "transaction",
]


def create_columns(transaction):
    columns = {
        "type": transaction.__class__.__name__,
        "fitid": transaction.fitid,
        "dttrade": transaction.dttrade,
        "memo": transaction.memo,
        "uniqueid": transaction.uniqueid,
        "uniqueidtype": transaction.uniqueidtype,
        # "incometype": transaction.incometype,
        "total": transaction.total,
        "currate": transaction.currate,
        "cursym": transaction.cursym,
        # "transaction": transaction,
    }
    return columns


def create_rows(input):
    rows = []
    ofx_tree = OFXTree()
    with open(input, "rb") as f:
        ofx_tree.parse(f)
        ofx = ofx_tree.convert()
        stmts = ofx.statements
        for stmt in stmts:
            transactions = stmt.transactions
            rows = create_rows_from_transactions(transactions)
    return rows


def create_rows_from_transactions(transactions):
    rows = []
    for transaction in transactions:
        columns = create_columns(transaction)
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
