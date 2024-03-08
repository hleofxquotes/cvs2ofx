import os
import unittest

from ofxtools import OFXTree
from ofxtools.models import BUYMF, BUYSTOCK, INCOME

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.my_data_path = os.path.join(THIS_DIR, os.pardir, "private/FIDELITY20230125131402309731.ofx")
        parser = OFXTree()
        with open(cls.my_data_path, 'rb') as f:
            parser.parse(f)
            cls.fidelity_ofx = parser.convert()

    @classmethod
    def tearDownClass(cls):
        cls.my_data_path = None
        cls.fidelity_ofx = None

    def test_securities(self):
        ofx = self.fidelity_ofx
        self.assertIsNotNone(ofx)

        securities = ofx.securities
        self.assertIsNotNone(securities)
        self.assertEqual(14, len(securities))
        for security in securities:
            print(security)
            print(security.uniqueid)
            print(security.uniqueidtype)
            print(security.secname)
            print(security.ticker)
            print(security.unitprice)
            print(security.dtasof)
            # print(security.currate)
            print(security.cursym)
            # print(security.mftype)
            # print(security.dtyieldasof)
            #print(security.tzinfo)

    def test_transactions(self):
        ofx = self.fidelity_ofx
        self.assertIsNotNone(ofx)

        stmts = ofx.statements
        self.assertIsNotNone(stmts)
        for stmt in stmts:
            transactions = stmt.transactions
            self.assertEqual(12, len(transactions))
            mutual_funds = []
            stocks = []
            income = []
            others = []
            for transaction in transactions:
                if isinstance(transaction, BUYMF):
                    mutual_funds.append(transaction)
                elif isinstance(transaction, BUYSTOCK):
                    stocks.append(transaction)
                elif isinstance(transaction, INCOME):
                    income.append(transaction)
                else:
                    others.append(transaction)
            self.assertEqual(4, len(mutual_funds))
            self.assertEqual(1, len(stocks))
            self.assertEqual(7, len(income))
            self.assertEqual(0, len(others))


if __name__ == '__main__':
    unittest.main()
