import unittest
from unittest.mock import patch
import mysql.connector
from main_test import DB_CONFIG, pridat_ukol, aktualizovat_ukol, odstranit_ukol, setup_database

# Úprava konfigurace pro testovací DB
TEST_DB_CONFIG = DB_CONFIG.copy()
TEST_DB_CONFIG['database'] = 'Project_5_test' 

class TestSpravceUkolu(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Spustí se jednou před všemi testy - vytvoří tabulku v testovací DB."""
        cls.conn = mysql.connector.connect(**TEST_DB_CONFIG)
        setup_database(cls.conn)

    @classmethod
    def tearDownClass(cls):
        """Spustí se po všech testech - zavře spojení."""
        cls.conn.close()

    def tearDown(self):
        """Smaže testovací data po každém jednotlivém testu."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ukoly")
        self.conn.commit()
        cursor.close()

    # --- TESTY: PŘIDÁNÍ ÚKOLU ---

    @patch('builtins.input', side_effect=['Testovací úkol', 'Popis testu', '1'])
    def test_pridat_ukol_pozitivni(self, mock_input):
        """Pozitivní: Ověří, že se úkol skutečně uloží do DB."""
        pridat_ukol(self.conn)
        cursor = self.conn.cursor()
        cursor.execute("SELECT nazev FROM ukoly WHERE nazev = 'Testovací úkol'")
        vysledek = cursor.fetchone()
        self.assertIsNotNone(vysledek)
        self.assertEqual(vysledek[0], 'Testovací úkol')

    @patch('builtins.input', side_effect=['', 'Bez nazvu', '1', 'Opraveny nazev', 'Popis', '1'])
    def test_pridat_ukol_negativni(self, mock_input):
        """Negativní: Ověří, že program nepustí prázdný název (díky tvé while validaci)."""
        pridat_ukol(self.conn)
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM ukoly")
        self.assertEqual(cursor.fetchone()[0], 1) # Úkol se přidal až po opravě názvu

    # --- TESTY: AKTUALIZACE ÚKOLU ---

    def test_aktualizovat_ukol_pozitivni(self):
        """Pozitivní: Změní stav existujícího úkolu."""
        # Nejdřív vložíme data přímo
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO ukoly (id, nazev, popis, stav) VALUES (10, 'Ukol', 'Popis', 'nezahájeno')")
        self.conn.commit()

        with patch('builtins.input', side_effect=['10', '2']): # ID 10, stav 2 (probíhá)
            aktualizovat_ukol(self.conn)
        
        cursor.execute("SELECT stav FROM ukoly WHERE id = 10")
        self.assertEqual(cursor.fetchone()[0], 'probíhá')

    @patch('builtins.input', side_effect=['999', 'q'])
    def test_aktualizovat_ukol_negativni(self, mock_input):
        """Negativní: Zadání neexistujícího ID (999) a následné ukončení."""
        # Vložíme jeden úkol, aby funkce nebyla prázdná
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO ukoly (id, nazev, popis) VALUES (1, 'X', 'Y')")
        self.conn.commit()

        # Funkce by měla vypsat chybu a díky 'q' skončit bez pádu
        aktualizovat_ukol(self.conn)
        cursor.execute("SELECT stav FROM ukoly WHERE id = 1")
        self.assertEqual(cursor.fetchone()[0], 'nezahájeno') # Stav se nezměnil

    # --- TESTY: ODSTRANĚNÍ ÚKOLU ---

    def test_odstranit_ukol_pozitivni(self):
        """Pozitivní: Smaže úkol podle ID."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO ukoly (id, nazev, popis) VALUES (50, 'Na smazani', '...')")
        self.conn.commit()

        with patch('builtins.input', side_effect=['50', 'ano']):
            odstranit_ukol(self.conn)

        cursor.execute("SELECT * FROM ukoly WHERE id = 50")
        self.assertIsNone(cursor.fetchone())

    @patch('builtins.input', side_effect=['888', 'q'])
    def test_odstranit_ukol_negativni(self, mock_input):
        """Negativní: Pokus o smazání neexistujícího ID."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO ukoly (id, nazev, popis) VALUES (1, 'Nechat', '...')")
        self.conn.commit()

        odstranit_ukol(self.conn)
        cursor.execute("SELECT count(*) FROM ukoly")
        self.assertEqual(cursor.fetchone()[0], 1) # Úkol tam stále je

if __name__ == '__main__':
    unittest.main()