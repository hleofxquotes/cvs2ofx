import os
from unittest import TestCase

from fidelity_ofx import FidelityOfx

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestFidelityOfx(TestCase):
    my_data_path = None
    fidelity_ofx = None

    @classmethod
    def setUpClass(cls):
        cls.my_data_path = os.path.join(THIS_DIR, os.pardir, "private/FIDELITY20230125131402309731.ofx")
        cls.fidelity_ofx = FidelityOfx(cls.my_data_path)

    @classmethod
    def tearDownClass(cls):
        cls.my_data_path = None
        cls.fidelity_ofx = None

    def test_parse(self):
        self.assertTrue(self.my_data_path is not None)

    def test_transactions(self):
        transactions = self.fidelity_ofx.get_transactions()
        self.assertEqual(5, len(transactions))
        self.assertEqual(4, len(self.fidelity_ofx.get_buymf(transactions)))
        self.assertEqual(0, len(self.fidelity_ofx.get_sellmf(transactions)))
        self.assertEqual(2, len(self.fidelity_ofx.get_buystock(transactions)))
        self.assertEqual(0, len(self.fidelity_ofx.get_sellstock(transactions)))
        self.assertEqual(7, len(self.fidelity_ofx.get_income(transactions)))

        positions = self.fidelity_ofx.get_positions()
        self.assertEqual(2, len(positions))
        self.assertEqual(11, len(self.fidelity_ofx.get_posmf(positions)))
        self.assertEqual(2, len(self.fidelity_ofx.get_posstock(positions)))

        securities = self.fidelity_ofx.get_securities()
        self.assertEqual(2, len(securities))
        self.assertEqual(12, len(self.fidelity_ofx.get_mfinfo(securities)))
        self.assertEqual(2, len(self.fidelity_ofx.get_stockinfo(securities)))

