from ofxtools.models import *
from ofxtools.utils import UTC
from decimal import Decimal
from datetime import datetime
import xml.etree.ElementTree as ET
from ofxtools.header import make_header

ledgerbal = LEDGERBAL(balamt=Decimal("150.65"), dtasof=datetime(2015, 1, 1, tzinfo=UTC))
acctfrom = BANKACCTFROM(
    bankid="123456789", acctid="23456", accttype="CHECKING"
)  # OFX Section 11.3.1
stmtrs = STMTRS(curdef="USD", bankacctfrom=acctfrom, ledgerbal=ledgerbal)
status = STATUS(code=0, severity="INFO")
stmttrnrs = STMTTRNRS(trnuid="5678", status=status, stmtrs=stmtrs)
bankmsgsrs = BANKMSGSRSV1(stmttrnrs)
fi = FI(org="Illuminati", fid="666")  # Required for Quicken compatibility
sonrs = SONRS(
    status=status, dtserver=datetime(2015, 1, 2, 17, tzinfo=UTC), language="ENG", fi=fi
)
signonmsgs = SIGNONMSGSRSV1(sonrs=sonrs)
ofx = OFX(signonmsgsrsv1=signonmsgs, bankmsgsrsv1=bankmsgsrs)
root = ofx.to_etree()
message = ET.tostring(root).decode()
header = str(make_header(version=220))
response = header + message
print(response)
