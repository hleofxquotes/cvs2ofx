# 						<INVBUY>
# 							<INVTRAN>
# 								<FITID>ABCDEFGH36401320221229</FITID>
# 								<DTTRADE>20221229120000</DTTRADE>
# 								<MEMO>REINVESTMENT</MEMO>
# 							</INVTRAN>
# 							<SECID>
# 								<UNIQUEID>31634R109</UNIQUEID>
# 								<UNIQUEIDTYPE>CUSIP</UNIQUEIDTYPE>
# 							</SECID>
# 							<UNITS>+0000000000011.17200</UNITS>
# 							<UNITPRICE>000000047.300000000</UNITPRICE>
# 							<COMMISSION>+00000000000000.0000</COMMISSION>
# 							<FEES>+00000000000000.0000</FEES>
# 							<TOTAL>-00000000000528.4200</TOTAL>
# 							<CURRENCY>
# 								<CURRATE>1.00</CURRATE>
# 								<CURSYM>USD</CURSYM>
# 							</CURRENCY>
# 							<SUBACCTSEC>CASH</SUBACCTSEC>
# 							<SUBACCTFUND>CASH</SUBACCTFUND>
# 						</INVBUY>
from ofxtools import models


class SecId:
    def __init__(
        self,
        symbol,
        type,
    ) -> None:
        super().__init__()
        self.model = models.SECID(
            uniqueid=symbol,
            uniqueidtype=type,
        )


class InvTran:
    def __init__(
        self,
        fitid,
        dttrade,
        memo=None,
    ) -> None:
        super().__init__()
        self.model = models.INVTRAN(fitid=fitid, dttrade=dttrade, memo=memo)


class InvBuy:
    def __init__(self) -> None:
        super().__init__()
        self.model = models.INVBUY(
            invtran

        )
