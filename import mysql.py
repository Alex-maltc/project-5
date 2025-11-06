import mysql.connector
from mysql.connector import Error

# --- KONFIGURACE DATABÁZE ---
DB_CONFIG = {
    'host': 'localhost',  # Změňte, pokud je MySQL server jinde
    'database': 'Project 5',
    'user': 'root',       # Změňte na vaše uživatelské jméno
    'password': '11111111' # Změňte na vaše heslo
}

def create_db_connection():
    """Vytvoří a vrátí spojení k databázi."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Chyba při připojování k MySQL: {e}")
        return None

def setup_database(conn):
    """Vytvoří tabulku 'ukoly', pokud neexistuje."""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT
            );
        """)
        conn.commit()
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")
    finally:
        cursor.close()

def hlavni_menu():
    """Zobrazí hlavní menu a vrátí volbu uživatele. Nyní se 4 volbami."""
    print("\n--- Správce úkolů - Hlavní menu ---")
    print("1. Přidat nový úkol")
    print("2. Zobrazit všechny úkoly")
    print("3. Aktualizovat úkol")     # NOVÁ VOLBA
    print("4. Odstranit úkol")
    print("5. Konec programu")         # Konec je nyní volba 5
    
    volba = input("Vyberte možnost (1-5): ")
    return volba

# ------------------------------
# ZŮSTÁVÁ STEJNÉ
# ------------------------------
def pridat_ukol(conn):
    """Vloží nový úkol do tabulky ukoly."""
    nazev = input("Zadejte název úkolu: ")
    popis = input("Zadejte popis úkolu: ")
    
    query = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
    data = (nazev, popis)
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, data)
        conn.commit()
        print(f"Úkol '{nazev}' byl úspěšně přidán do databáze.")
    except Error as e:
        print(f"Chyba při přidávání úkolu: {e}")
    finally:
        cursor.close()

def zobrazit_ukoly(conn):
    """Načte a zobrazí všechny úkoly z databáze."""
    query = "SELECT id, nazev, popis FROM ukoly ORDER BY id"
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        ukoly = cursor.fetchall()

        print("\nSeznam úkolů:")
        if not ukoly:
            print("Seznam úkolů je prázdný.")
        else:
            for id, nazev, popis in ukoly:
                print(f"{id}. {nazev} - {popis}")
    except Error as e:
        print(f"Chyba při načítání úkolů: {e}")
    finally:
        cursor.close()
    
    return ukoly
    
# ------------------------------
# 3. FUNKCE AKTUALIZOVAT ÚKOL
# ------------------------------
def aktualizovat_ukol(conn):
    """Umožní uživateli aktualizovat název a popis úkolu podle ID."""
    
    # Zobrazíme úkoly pro výběr
    ukoly = zobrazit_ukoly(conn)
    if not ukoly:
        print("Není co aktualizovat.")
        return

    try:
        # Získání ID úkolu
        id_str = input("\nZadejte ID úkolu, který chcete aktualizovat: ")
        ukol_id = int(id_str)
        
        # Získání nových dat
        novy_nazev = input(f"Zadejte nový název pro úkol {ukol_id} (nebo stiskněte Enter pro zachování původního): ")
        novy_popis = input(f"Zadejte nový popis pro úkol {ukol_id} (nebo stiskněte Enter pro zachování původního): ")
        
        # Sestavení SQL dotazu - aktualizujeme pouze pokud je zadaná nová hodnota
        
        set_clauses = []
        data = []
        
        if novy_nazev.strip():
            set_clauses.append("nazev = %s")
            data.append(novy_nazev)
            
        if novy_popis.strip():
            set_clauses.append("popis = %s")
            data.append(novy_popis)
            
        if not set_clauses:
            print("Nebyl zadán žádný nový název ani popis. Aktualizace zrušena.")
            return

        # Dokončení dotazu
        query = f"UPDATE ukoly SET {', '.join(set_clauses)} WHERE id = %s"
        data.append(ukol_id) # ID jde na konec pro WHERE klauzuli

        cursor = conn.cursor()
        cursor.execute(query, tuple(data))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Úkol s ID '{ukol_id}' byl úspěšně aktualizován.")
        else:
            print(f"Chyba: Úkol s ID '{ukol_id}' nebyl nalezen.")

    except ValueError:
        print("Chyba: Nebylo zadáno platné ID úkolu.")
    except Error as e:
        print(f"Chyba při aktualizaci úkolu: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

# ------------------------------
# 4. FUNKCE ODSTRANIT ÚKOL
# ------------------------------
def odstranit_ukol(conn):
    """Odstraní úkol podle ID zadaného uživatelem."""
    
    ukoly = zobrazit_ukoly(conn)
    if not ukoly:
        print("Není co odstranit.")
        return

    try:
        id_str = input("\nZadejte ID úkolu, který chcete odstranit: ")
        ukol_id = int(id_str)
        
        query = "DELETE FROM ukoly WHERE id = %s"
        cursor = conn.cursor()
        
        cursor.execute(query, (ukol_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Úkol s ID '{ukol_id}' byl odstraněn.")
        else:
            print(f"Chyba: Úkol s ID '{ukol_id}' nebyl nalezen.")

    except ValueError:
        print("Chyba: Nebylo zadáno platné číslo pro ID.")
    except Error as e:
        print(f"Chyba při odstraňování úkolu: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

# ------------------------------
# HLAVNÍ FUNKCE PROGRAMU
# ------------------------------
def main():
    """Hlavní funkce řídící běh programu."""
    
    conn = create_db_connection()
    
    if conn is None:
        print("\nNelze se připojit k databázi. Ukončuji program.")
        return

    setup_database(conn)

    # Hlavní smyčka programu
    while True:
        volba = hlavni_menu()
        
        if volba == '1':
            pridat_ukol(conn)
            input("\nStiskněte Enter pro návrat do menu...")
            
        elif volba == '2':
            zobrazit_ukoly(conn)
            input("\nStiskněte Enter pro návrat do menu...")
            
        elif volba == '3':
            aktualizovat_ukol(conn)
            input("\nStiskněte Enter pro návrat do menu...")

        elif volba == '4':
            odstranit_ukol(conn) 
            input("\nStiskněte Enter pro návrat do menu...")

        elif volba == '5':
            print("\nUkončuji program. Nashledanou!")
            break 
            
        else:
            print("\nNeplatná volba. Zadejte prosím číslo od 1 do 5.")
            input("\nStiskněte Enter pro návrat do menu...")

    if conn and conn.is_connected():
        conn.close()

# Spuštění programu
if __name__ == "__main__":
    main()