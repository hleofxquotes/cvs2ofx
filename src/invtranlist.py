import argparse
import csv
import hashlib
import json
import uuid
import xml.dom.minidom
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

import pytz as pytz

# local imports
from ofxtools import models
from ofxtools.header import make_header
from ofxtools.utils import UTC

DEFAULT_OFX_VERSION = 202

DEFAULT_BROKER_ID = "123456789"

DEFAULT_CURRENCY = "USD"


def create_data_csv_rows_from_file(filename):
    data_csv_rows = []
    with open(filename, "r") as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            # print(dict(row))
            data_csv_rows.append(dict(row))
    return data_csv_rows


# def create_data_csv_rows_hard_code():
#     data_csv_rows = []
#     data_csv_rows.append(
#         {
#             "txn_type": "BUYSTOCK",
#             # datetime(2022, 8, 25, tzinfo=UTC),
#             # datetime.strptime("2020-01-01 14:00", "%Y-%m-%d %H:%M")
#             "trade_date": "2022/08/25",
#             "symbol": "TSLA",
#             "units": "100",
#             "unitprice": "50.00",
#             # BUY total is NEGATIVE
#             # SELL total is POSITIVE
#             "total": "-5000.00",
#         },
#     )
#     data_csv_rows.append(
#         {
#             "txn_type": "SELLSTOCK",
#             # datetime(2022, 7, 12, tzinfo=UTC),
#             "trade_date": "2022/07/12",
#             "symbol": "AAPL",
#             "units": "10",
#             "unitprice": "129.93",
#             # SELL total is POSITIVE
#             "total": "1299.30",
#         },
#     )
#     data_csv_rows.append(
#         {
#             "txn_type": "BUYMF",
#             # datetime(2022, 6, 11, tzinfo=UTC),
#             "trade_date": "2022/06/11",
#             "symbol": "VTI",
#             "units": "35.00",
#             "unitprice": "191.19",
#             # BUY total is NEGATIVE
#             "total": "-6691.65",
#         },
#     )
#     data_csv_rows.append(
#         {
#             "txn_type": "SELLMF",
#             # datetime(2022, 5, 8, tzinfo=UTC),
#             "trade_date": "2022/05/08",
#             "symbol": "VOO",
#             "units": "12.00",
#             "unitprice": "351.34",
#             # SELL total is POSITIVE
#             "total": "4216.08",
#         },
#     )
#     return data_csv_rows


# def create_data_csv_rows():
#     # return create_data_csv_rows_hard_code()
#     return create_data_csv_rows_from_file("../data/example1.csv")

DEFAULT_TXN_TYPE = "BUYSTOCK"
DEFAULT_UNIQUE_ID_TYPE = "TICKER"
DEFAULT_SUB_ACCT_SEC = "CASH"
DEFAULT_SUB_ACCT_FUND = "CASH"


class InvestmentTransaction:
    def __init__(
        self,
        trade_date,
        symbol,
        units,
        unitprice,
        total,
        fitid=None,
        txn_type=DEFAULT_TXN_TYPE,
        uniqueidtype=DEFAULT_UNIQUE_ID_TYPE,
        subacctsec=DEFAULT_SUB_ACCT_SEC,
        subacctfund=DEFAULT_SUB_ACCT_FUND,
    ):
        self.trade_date = trade_date
        self.symbol = symbol
        self.units = units
        self.unitprice = unitprice
        self.total = total
        if not fitid:
            fitid = self.generate_fitid()
        self.fitid = fitid
        # BUYSTOCK, SELLSTOCK, BUYMF, SELLMF
        self.txn_type = txn_type
        self.uniqueidtype = uniqueidtype
        self.subacctsec = subacctsec
        self.subacctfund = subacctfund

    def generate_fitid(self):
        return str(uuid.uuid4())

    def ofx(self):
        match self.txn_type:
            case "BUYSTOCK":
                return self.create_buystock()
            case "SELLSTOCK":
                return self.create_sellstock()
            case "BUYMF":
                return self.create_buymf()
            case "SELLMF":
                return self.create_sellmf()
        return None

    def create_secid(self):
        return models.SECID(
            # Unique identifier for the security. CUSIP for US FIs. A-32
            # uniqueid="123456789",
            uniqueid=self.symbol,
            # Name of standard used to identify the security i.e., “CUSIP” for FIs in the United
            # States, A-10
            # CUSIP, TICKER, OTHER, PRIVATE
            # uniqueidtype="CUSIP"
            uniqueidtype=self.uniqueidtype,
        )

    def create_invtran(self):
        return models.INVTRAN(
            # fitid="23321",
            fitid=self.fitid,
            # dttrade=datetime(2005, 8, 25, tzinfo=UTC),
            dttrade=self.trade_date,
            # dtsettle=datetime(2005, 8, 28, tzinfo=UTC),
        )

    def create_buystock(self):
        return models.BUYSTOCK(
            invbuy=models.INVBUY(
                invtran=self.create_invtran(),
                # Security identifier
                # 13.8.1 Security Identification <SECID>
                secid=self.create_secid(),
                # units=Decimal("100"),
                units=self.units,
                # unitprice=Decimal("50.00"),
                unitprice=self.unitprice,
                # commission=Decimal("25.00"),
                # total=Decimal("-5025.00"),
                total=self.total,
                # subacctsec="CASH",
                subacctsec=self.subacctsec,
                # subacctfund="CASH",
                subacctfund=self.subacctfund,
            ),
            buytype="BUY",
        )

    def create_sellstock(self):
        return models.SELLSTOCK(
            # 13.9.2.4.3 Investment Buy/Sell Aggregates <INVBUY>/<INVSELL>
            invsell=models.INVSELL(
                invtran=self.create_invtran(),
                # Security identifier
                # 13.8.1 Security Identification <SECID>
                secid=self.create_secid(),
                # units=Decimal("100"),
                units=self.units,
                # unitprice=Decimal("50.00"),
                unitprice=self.unitprice,
                # commission=Decimal("25.00"),
                # total=Decimal("-5025.00"),
                total=self.total,
                # subacctsec="CASH",
                subacctsec=self.subacctsec,
                # subacctfund="CASH",
                subacctfund=self.subacctfund,
            ),
            selltype="SELL",
        )

    def create_buymf(self):
        return models.BUYMF(
            invbuy=models.INVBUY(
                invtran=self.create_invtran(),
                # Security identifier
                # 13.8.1 Security Identification <SECID>
                secid=self.create_secid(),
                # units=Decimal("100"),
                units=self.units,
                # unitprice=Decimal("50.00"),
                unitprice=self.unitprice,
                # commission=Decimal("25.00"),
                # total=Decimal("-5025.00"),
                total=self.total,
                # subacctsec="CASH",
                subacctsec=self.subacctsec,
                # subacctfund="CASH",
                subacctfund=self.subacctfund,
                # loanid="2",
                # loanprincipal=Decimal("277.5700"),
                # loaninterest=Decimal("0.0000"),
                # inv401ksource="ROLLOVER",
                # dtpayroll=datetime(2005, 1, 14, 5, tzinfo=UTC),
                # prioryearcontrib=False,
            ),
            buytype="BUY",
        )

    def create_sellmf(self):
        return models.SELLMF(
            invsell=models.INVSELL(
                invtran=self.create_invtran(),
                # Security identifier
                # 13.8.1 Security Identification <SECID>
                secid=self.create_secid(),
                # units=Decimal("100"),
                units=self.units,
                # unitprice=Decimal("50.00"),
                unitprice=self.unitprice,
                # commission=Decimal("25.00"),
                # total=Decimal("-5025.00"),
                total=self.total,
                # subacctsec="CASH",
                subacctsec=self.subacctsec,
                # subacctfund="CASH",
                subacctfund=self.subacctfund,
                # loanid="2",
                # loanprincipal=Decimal("277.5700"),
                # loaninterest=Decimal("0.0000"),
                # inv401ksource="ROLLOVER",
                # dtpayroll=datetime(2005, 1, 14, 5, tzinfo=UTC),
                # prioryearcontrib=False,
            ),
            selltype="SELL",
        )


def convert_to_datetime(date_string, date_string_format="%Y/%m/%d"):
    # datetime.strptime("2020-01-01 14:00", "%Y-%m-%d %H:%M")
    d = datetime.strptime(date_string, date_string_format)
    return datetime(d.year, d.month, d.day, tzinfo=UTC)


def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def create_fitid(cols, row_number, fitids):
    fitid = dict_hash(cols)
    if fitid in fitids:
        fitid = fitid + "_" + row_number

    fitids.add(fitid)

    return fitid


def create_transactions(data_csv_rows, date_string_format):
    dtstart = None
    dtend = None

    row_number = 0
    txns = {}
    transactions = []
    fitids = set()
    for cols in data_csv_rows:
        row_number = row_number + 1
        txn = InvestmentTransaction(
            txn_type=cols["txn_type"],
            trade_date=convert_to_datetime(cols["trade_date"], date_string_format),
            symbol=cols["symbol"],
            units=Decimal(cols["units"]),
            unitprice=Decimal(cols["unitprice"]),
            # BUY total is NEGATIVE
            # SELL total is POSITIVE
            total=Decimal(cols["total"]),
        )
        txn.fitid = create_fitid(cols, row_number, fitids)

        trade_date = txn.trade_date
        if dtstart is None:
            dtstart = trade_date
        if dtend is None:
            dtend = trade_date
        dtstart = min(dtstart, trade_date)
        dtend = max(dtend, trade_date)

        if not txn.symbol in txns:
            txns[txn.symbol] = txn

        transactions.append(txn.ofx())

    secinfo = []
    for symbol in txns:
        tnx = txns[symbol]
        match tnx.txn_type:
            case "BUYSTOCK":
                secinfo.append(
                    models.STOCKINFO(
                        secinfo=models.SECINFO(
                            secid=models.SECID(
                                uniqueid=tnx.symbol, uniqueidtype=DEFAULT_UNIQUE_ID_TYPE
                            ),
                            secname=tnx.symbol,
                            ticker=tnx.symbol,
                            # fiid="1024",
                        ),
                        # yld=Decimal("10"),
                        # assetclass="SMALLSTOCK",
                    )
                )
            case "SELLSTOCK":
                secinfo.append(
                    models.STOCKINFO(
                        secinfo=models.SECINFO(
                            secid=models.SECID(
                                uniqueid=tnx.symbol, uniqueidtype=DEFAULT_UNIQUE_ID_TYPE
                            ),
                            secname=tnx.symbol,
                            ticker=tnx.symbol,
                            # fiid="1024",
                        ),
                        # yld=Decimal("10"),
                        # assetclass="SMALLSTOCK",
                    )
                )
            case "BUYMF":
                secinfo.append(
                    models.MFINFO(
                        secinfo=models.SECINFO(
                            secid=models.SECID(
                                uniqueid=tnx.symbol, uniqueidtype=DEFAULT_UNIQUE_ID_TYPE
                            ),
                            secname=tnx.symbol,
                            ticker=tnx.symbol,
                            # fiid="1024",
                        ),
                        # yld=Decimal("10"),
                        # assetclass="SMALLSTOCK",
                    )
                )
            case "SELLMF":
                secinfo.append(
                    models.MFINFO(
                        secinfo=models.SECINFO(
                            secid=models.SECID(
                                uniqueid=tnx.symbol, uniqueidtype=DEFAULT_UNIQUE_ID_TYPE
                            ),
                            secname=tnx.symbol,
                            ticker=tnx.symbol,
                            # fiid="1024",
                        ),
                        # yld=Decimal("10"),
                        # assetclass="SMALLSTOCK",
                    )
                )

    return [transactions, secinfo, dtstart, dtend]


# 2.5.1.6 Signon Response <SONRS>
STATUS = models.STATUS(code=0, severity="INFO")
SONRS = models.SONRS(
    status=STATUS,
    # dtserver=datetime(2005, 10, 29, 10, 10, 3, tzinfo=UTC),
    dtserver=datetime.now(pytz.utc),
    language="ENG",
    # dtprofup=datetime(2004, 10, 29, 10, 10, 3, tzinfo=UTC),
    # dtacctup=datetime(2004, 10, 29, 10, 10, 3, tzinfo=UTC),
    # fi=models.FI(org="NCH", fid="1001"),
)
SIGNONMSGSRSV1 = models.SIGNONMSGSRSV1(sonrs=SONRS)


class InvestmentAccount:
    def __init__(self, brokerid, acctid):
        self.brokerid = brokerid
        self.acctid = acctid

    def ofx(self):
        # 13.6.1 Specifying the Investment Account <INVACCTFROM>
        return models.INVACCTFROM(
            # Unique identifier for the FI, A-22
            # brokerid="121099999",
            brokerid=self.brokerid,
            # Account number at FI, A-22
            # acctid="999988"
            acctid=self.acctid,
        )


def create_ofx_object(
    trnuid,
    transactions,
    secinfo,
    dtstart,
    dtend,
    dtasof,
    brokerid,
    acctid,
):
    # Begin transaction list (at most one)
    invtranlist = models.INVTRANLIST(
        *transactions,
        # Start date for transaction data, datetime
        dtstart=dtstart,
        # This is the value that should be sent in the next <DTSTART> request to insure
        # that no transactions are missed, datetime
        dtend=dtend,
    )
    # 13.9.2.2 Investment Statement Response <INVSTMTRS>
    invstmtrs = models.INVSTMTRS(
        # As of date & time for the statement download, datetime
        dtasof=dtasof,
        # Default currency for the statement, currsymbol
        curdef=DEFAULT_CURRENCY,
        # Which account at FI, see 13.6.1
        invacctfrom=InvestmentAccount(brokerid, acctid).ofx(),
        invtranlist=invtranlist,
    )

    seclistmsgsrsv1 = models.SECLISTMSGSRSV1(models.SECLIST(*secinfo))

    ofx = models.OFX(
        signonmsgsrsv1=SIGNONMSGSRSV1,
        invstmtmsgsrsv1=models.INVSTMTMSGSRSV1(
            # 13.9.2.1 Investment Statement Transaction Response <INVSTMTTRNRS>
            models.INVSTMTTRNRS(
                # Client-assigned globally unique ID for this transaction, trnuid
                # trnuid="1002",
                trnuid=trnuid,
                status=STATUS,
                # 13.9.2.2 Investment Statement Response <INVSTMTRS>
                invstmtrs=invstmtrs,
            )
        ),
        seclistmsgsrsv1=seclistmsgsrsv1,
    )
    return ofx


def create_ofx_string(ofx, pretty_print):
    root = ofx.to_etree()
    message = ET.tostring(root).decode()
    header = str(make_header(version=DEFAULT_OFX_VERSION))
    response = header + message
    if pretty_print:
        response = xml.dom.minidom.parseString(response).toprettyxml(indent="  ")
    return response


def main(args):
    print("# Reading input from file=%s" % args.input)

    # Start date for transaction data, datetime
    # dtstart = datetime(2023, 1, 5, 22, 25, 32, tzinfo=UTC)
    # This is the value that should be sent in the next <DTSTART> request to insure
    # that no transactions are missed, datetime
    # dtend = datetime(2023, 1, 31, 21, 25, 32, tzinfo=UTC)

    [transactions, secinfo, dtstart, dtend] = create_transactions(
        create_data_csv_rows_from_file(args.input), args.date_string_format
    )

    # Client-assigned globally unique ID for this transaction, trnuid
    if args.trnuid is None:
        trnuid = str(uuid.uuid4())
    else:
        trnuid = args.trnuid

    # As of date & time for the statement download, datetime
    # dtasof = datetime(2023, 1, 31, 21, 26, 5, tzinfo=UTC)
    dtasof = datetime.now(pytz.utc)
    # Unique identifier for the FI, A-22
    brokerid = DEFAULT_BROKER_ID
    # Account number at FI, A-22
    if args.brokerid is None:
        brokerid = DEFAULT_BROKER_ID
    else:
        brokerid = args.brokerid

    acctid = args.acctid

    pretty_print = args.pretty_print

    ofx = create_ofx_object(
        trnuid, transactions, secinfo, dtstart, dtend, dtasof, brokerid, acctid
    )
    response = create_ofx_string(ofx, pretty_print)
    with open(args.output, "w") as f:
        print("# Writing output to file=%s" % args.output)
        print(response, file=f)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True, help="Input file")
    parser.add_argument("--output", "-o", required=True, help="Output file")
    parser.add_argument(
        "--date_string_format", "-d", default="%Y/%m/%d", help="Date string format"
    )
    parser.add_argument(
        "--trnuid",
        "-t",
        required=False,
        help="Client-assigned globally unique ID for this transaction",
    )
    parser.add_argument(
        "--brokerid",
        "-b",
        required=False,
        help="Unique identifier for the FI, A-22",
    )
    parser.add_argument(
        "--acctid",
        "-a",
        required=True,
        help="Account number at FI, A-22",
    )
    parser.add_argument(
        "--pretty_print",
        "-p",
        default=False,
        action="store_true",
        help="Pretty print the output",
    )
    args = parser.parse_args()
    main(args)
