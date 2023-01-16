import argparse
import configparser
import csv
import glob
import hashlib
import json
import os
import sys
import uuid
import xml.dom.minidom
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any

# local imports
from ofxtools import models
from ofxtools.header import make_header


DEFAULT_CONFIG_SECTION = "invtranlist"

DEFAULT_CONFIG_FILENAME = os.environ.get(
    "INVTRANLIST_CONFIG", default="invtranlist.ini"
)

DEFAULT_OFX_VERSION = 202

DEFAULT_BROKER_ID = "123456789"

DEFAULT_CURRENCY = "USD"

LOCAL_TZINFO = datetime.now().astimezone().tzinfo


def create_data_csv_rows_from_file(filename):
    """
    Parse CSV filename and return a list of rows (each is dictionary of column's values)

    :param filename:
    :return:
    """

    data_csv_rows = []
    if filename is None:
        return [data_csv_rows, filename]

    print("# Reading input from file=%s" % filename)

    with open(filename, "r") as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            # print(dict(row))
            data_csv_rows.append(dict(row))
    return data_csv_rows


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
        memo="",
    ):
        """
        An investment transaction model.

        :param trade_date:
        :param symbol:
        :param units:
        :param unitprice:
        :param total:
        :param fitid:
        :param txn_type:
        :param uniqueidtype:
        :param subacctsec:
        :param subacctfund:
        :param memo:
        """
        self.trade_date = trade_date
        self.memo = memo
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
        """
        Fallback way to generate a fitid if one is not provided.

        :return:
        """
        return str(uuid.uuid4())

    def ofx(self):
        """
        Generate the OFX object from the model.

        :return:
        """
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
        """
        Create a SECID object which basically identify a security with symbol and type (such as TICKER)
        :return:
        """
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
        """
        Create an INVTRAN OFX object which has the transaction id and a trade date.

        :return:
        """
        return models.INVTRAN(
            # fitid="23321",
            fitid=self.fitid,
            # dttrade=datetime(2005, 8, 25, tzinfo=UTC),
            dttrade=self.trade_date,
            # dtsettle=datetime(2005, 8, 28, tzinfo=UTC),
            memo=self.memo,
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
    """
    Convert a date string using date_string_format.

    :param date_string:
    :param date_string_format:
    :return:
    """
    # datetime.strptime("2020-01-01 14:00", "%Y-%m-%d %H:%M")
    d = datetime.strptime(date_string, date_string_format)
    # tzinfo = UTC
    tzinfo = LOCAL_TZINFO
    return datetime(d.year, d.month, d.day, tzinfo=tzinfo)


def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def create_fitid(cols, row_number, fitids):
    """
    Create a fitid (transaction id) from the input (a row: or dictionary if column values).
    If there is a collision (we keep track of existing values in fitids), use row_number to resolve
    the conflict.

    :param cols:
    :param row_number:
    :param fitids:
    :return:
    """
    fitid = dict_hash(cols)
    if fitid in fitids:
        fitid = fitid + "_" + row_number

    fitids.add(fitid)

    return fitid


def ensure_sign(value, must_be_positive=True):
    """
    Ensure that a value has correct sign.

    :param value:
    :param must_be_positive:
    :return:
    """
    if must_be_positive:
        return +abs(value)
    else:
        return -abs(value)


def create_transactions(data_csv_rows, date_string_format):
    """
    Create a list of transactions from info in the list of data_csv_rows.

    :param data_csv_rows:
    :param date_string_format:
    :return:
    """
    dtstart = None
    dtend = None
    memo = None

    row_number = 0
    txns = {}
    transactions = []
    fitids = set()
    for cols in data_csv_rows:
        row_number = row_number + 1

        txn_type = cols["txn_type"]
        # Ensure sign correctness
        match txn_type:
            case "BUYSTOCK":
                # BUY units is POSITIVE
                units = ensure_sign(Decimal(cols["units"]))
                # BUY total is NEGATIVE
                total = ensure_sign(Decimal(cols["total"]), False)
            case "BUYMF":
                # BUY units is POSITIVE
                units = ensure_sign(Decimal(cols["units"]))
                # BUY total is NEGATIVE
                total = ensure_sign(Decimal(cols["total"]), False)
            case "SELLSTOCK":
                # SELL units is NEGATIVE
                units = ensure_sign(Decimal(cols["units"]), False)
                # SELL total is POSITIVE
                total = ensure_sign(Decimal(cols["total"]))
            case "SELLMF":
                # SELL units is NEGATIVE
                units = ensure_sign(Decimal(cols["units"]), False)
                # SELL total is POSITIVE
                total = ensure_sign(Decimal(cols["total"]))

        symbol = cols["symbol"]
        if "memo" in cols:
            memo = cols["memo"]
            if memo is None or len(memo) <= 0:
                memo = ""
        else:
            memo = ""

        txn = InvestmentTransaction(
            txn_type=txn_type,
            trade_date=convert_to_datetime(cols["trade_date"], date_string_format),
            symbol=symbol,
            # BUY units is POSITIVE
            # SELL units is NEGATIVE
            units=units,
            unitprice=Decimal(cols["unitprice"]),
            # BUY total is NEGATIVE
            # SELL total is POSITIVE
            total=total,
            memo=memo,
        )
        txn.fitid = create_fitid(cols, row_number, fitids)

        trade_date = txn.trade_date
        if dtstart is None:
            dtstart = trade_date
        if dtend is None:
            dtend = trade_date
        dtstart = min(dtstart, trade_date)
        dtend = max(dtend, trade_date)

        if txn.symbol not in txns:
            txns[txn.symbol] = txn

        transactions.append(txn.ofx())

    secinfo = create_secinfo(txns)

    return [transactions, secinfo, dtstart, dtend]


def create_secinfo(txns):
    """
    Create list of secinfo (such as STOCKINFO, MFINFO ...) from the list of transactions.

    :param txns:
    :return:
    """
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
    return secinfo


# 2.5.1.6 Signon Response <SONRS>
STATUS = models.STATUS(code=0, severity="INFO")
SONRS = models.SONRS(
    status=STATUS,
    # dtserver=datetime(2005, 10, 29, 10, 10, 3, tzinfo=UTC),
    dtserver=datetime.now(LOCAL_TZINFO),
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
    """
    Create an OFX object (our model).

    :param trnuid:
    :param transactions:
    :param secinfo:
    :param dtstart:
    :param dtend:
    :param dtasof:
    :param brokerid:
    :param acctid:
    :return:
    """
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
    """
    Generate the OFX output from our object. If pretty_print is true, will attempt to
    output the XML in user-friendly format.

    :param ofx:
    :param pretty_print:
    :return:
    """
    root = ofx.to_etree()
    message = ET.tostring(root).decode()
    header = str(make_header(version=DEFAULT_OFX_VERSION))
    response = header + message
    if pretty_print:
        response = xml.dom.minidom.parseString(response).toprettyxml(indent="  ")
    return response


def main(args):
    """
    Read CSV file input and generate an OFX file

    :param args:
    """

    # Start date for transaction data, datetime
    # dtstart = datetime(2023, 1, 5, 22, 25, 32, tzinfo=UTC)
    # This is the value that should be sent in the next <DTSTART> request to insure
    # that no transactions are missed, datetime
    # dtend = datetime(2023, 1, 31, 21, 25, 32, tzinfo=UTC)

    # If user specified a directory, then find the latest *.csv file in that directory
    input_filename = args.input
    if os.path.isdir(input_filename):
        folder_path = input_filename
        files_path = os.path.join(folder_path, "*.csv")
        files = sorted(glob.iglob(files_path), key=os.path.getmtime, reverse=True)
        if len(files) > 0:
            input_filename = files[0]
        else:
            input_filename = None
        # print("# Will use input file=%s" % filename)

    if input_filename is None:
        print("# ERROR, input_file is None.")
        return

    [transactions, secinfo, dtstart, dtend] = create_transactions(
        create_data_csv_rows_from_file(input_filename), args.date_string_format
    )

    # Client-assigned globally unique ID for this transaction, trnuid
    if args.trnuid is None:
        trnuid = str(uuid.uuid4())
    else:
        trnuid = args.trnuid

    # As of date & time for the statement download, datetime
    # dtasof = datetime(2023, 1, 31, 21, 26, 5, tzinfo=UTC)
    dtasof = datetime.now(LOCAL_TZINFO)

    # Unique identifier for the FI, A-22
    brokerid = DEFAULT_BROKER_ID
    if args.brokerid is None:
        brokerid = DEFAULT_BROKER_ID
    else:
        brokerid = args.brokerid

    # Account number at FI, A-22
    acctid = args.acctid

    pretty_print = args.pretty_print

    ofx = create_ofx_object(
        trnuid, transactions, secinfo, dtstart, dtend, dtasof, brokerid, acctid
    )
    response = create_ofx_string(ofx, pretty_print)
    output_filename = args.output
    write_response(output_filename, input_filename, response)


def write_response(output_filename, input_filename, response):

    # if user specified an output directory then use the input_filename as template for
    # output filename
    # input_filename: abc.csv
    # output_filename: abc.ofx
    if os.path.isdir(output_filename):
        output_dir = os.path.abspath(output_filename)
        prefix = Path(os.path.abspath(input_filename)).stem
        output_filename = os.path.join(output_dir, prefix + ".ofx")

    # Write out the OFX output
    with open(output_filename, "w") as f:
        print("# Writing output to file=%s" % output_filename)
        print(response, file=f)


# Press the green button in the gutter to run the script.
def config_to_args(config, section):
    my_args = []
    try:
        # section = DEFAULT_CONFIG_SECTION
        options = config.options(section)
        for option in options:
            my_args.append("--" + option)
            value = config.get(section, option)
            if value and len(value) > 0:
                my_args.append(value)
    except configparser.NoSectionError:
        pass

    return my_args


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
