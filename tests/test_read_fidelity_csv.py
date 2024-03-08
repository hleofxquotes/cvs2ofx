import os
from unittest import TestCase

from read_fidelity_csv import FidelityMapper, FidelityCsv

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestFidelityMapper(TestCase):
    my_data_path = None
    fidelity_mapper = None

    @classmethod
    def setUpClass(cls):
        cls.my_data_path = os.path.join(THIS_DIR, os.pardir, "data/fidelity_mapper.csv")
        cls.fidelity_mapper = FidelityMapper(cls.my_data_path)

    @classmethod
    def tearDownClass(cls):
        cls.my_data_path = None
        cls.fidelity_mapper = None

    def test_parse(self):
        self.assertTrue(self.my_data_path is not None)

    def test_get_symbol_type(self):
        self.assertEqual(self.fidelity_mapper.get_symbol_type("FBALX"), "MF")
        self.assertNotEqual(self.fidelity_mapper.get_symbol_type("FBALX"), "STOCK")
        self.assertEqual(self.fidelity_mapper.get_symbol_type("XYZ"), "UNKNOWN")
        self.assertEqual(self.fidelity_mapper.get_symbol_type("AAPL"), "STOCK")
        self.assertEqual(self.fidelity_mapper.get_symbol_type("TSLA"), "STOCK")


class TestFidelityCsv(TestCase):
    my_data_path = None
    fidelity_mapper = None

    def __init__(self, fidelity_csv=None):
        self.fidelity_csv = fidelity_csv
        
    @classmethod
    def setUpClass(cls):
        cls.my_data_path = os.path.join(THIS_DIR, os.pardir, "data/fidelity_mapper.csv")
        cls.fidelity_mapper = FidelityMapper(cls.my_data_path)

    def test_get_action(self):
        fidelity_mapper = FidelityMapper()
        filename = os.path.join(THIS_DIR, os.pardir, "private/History_for_Account_#########.csv")
        header_lineno = 3
        self.fidelity_csv = FidelityCsv(filename, fidelity_mapper, header_lineno)

    def test_parse_fidelity_history_for_account(self):
        self.assertIsNotNone(self.fidelity_csv)
