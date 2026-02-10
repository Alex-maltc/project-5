import mysql.connector
from mysql.connector import Error

# --- KONFIGURACE DATABÁZE ---
DB_CONFIG = {
    'host': '127.0.0.1',  # Změňte, pokud je MySQL server jinde
    'database': 'Project_5',
    'user': 'root',      # Změňte na vaše uživatelské jméno
    'password': '2020' # Změňte na vaše heslo
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
    """Vytvoří tabulku 'ukoly' s rozšířenými sloupci, pokud neexistuje."""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav ENUM('nezahájeno', 'probíhá', 'hotovo') DEFAULT 'nezahájeno',
                datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("Tabulka 'ukoly' je připravena.")
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")
    finally:
        cursor.close()

def pridat_ukol(conn):
    """Vloží nový úkol. Stav je defaultně 'nezahájeno'."""
    print("\n--- Přidání nového úkolu ---")
    nazev = input("Název: ")
    popis = input("Popis: ")
    
    # Nabídka stavů
    print("Vyberte stav: 1. nezahájeno (default), 2. probíhá, 3. hotovo")
    volba_stavu = input("Volba (1-3): ")
    stavy_map = {'1': 'nezahájeno', '2': 'probíhá', '3': 'hotovo'}
    stav = stavy_map.get(volba_stavu, 'nezahájeno')

    query = "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    try:
        cursor.execute(query, (nazev, popis, stav))
        conn.commit()
        print(f"Úkol '{nazev}' byl přidán.")
    except Error as e:
        print(f"Chyba: {e}")
    finally:
        cursor.close()

def zobrazit_ukoly(conn):
    """Zobrazí úkoly včetně stavu a data vytvoření."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nazev, popis, stav, datum_vytvoreni FROM ukoly")
        ukoly = cursor.fetchall()

        print(f"\n{'ID':<3} | {'NÁZEV':<15} | {'STAV':<12} | {'VYTVOŘENO':<19}")
        print("-" * 60)
        
        if not ukoly:
            print("Seznam je prázdný.")
        else:
            for u_id, nazev, popis, stav, datum in ukoly:
                # datum formátujeme na čitelný text
                cas = datum.strftime("%d.%m.%Y %H:%M")
                print(f"{u_id:<3} | {nazev:<15} | {stav:<12} | {cas}")
        return ukoly
    except Error as e:
        print(f"Chyba: {e}")
    finally:
        cursor.close()

def aktualizovat_ukol(conn):
    """Umožní změnit název, popis i stav úkolu."""
    ukoly = zobrazit_ukoly(conn)
    if not ukoly: return

    try:
        u_id = int(input("\nZadejte ID úkolu pro změnu: "))
        novy_nazev = input("Nový název (Enter pro přeskočení): ")
        novy_popis = input("Nový popis (Enter pro přeskočení): ")
        print("Nový stav: 1. nezahájeno, 2. probíhá, 3. hotovo (Enter pro přeskočení)")
        v_stav = input("Volba: ")
        
        stavy_map = {'1': 'nezahájeno', '2': 'probíhá', '3': 'hotovo'}
        
        updates = []
        params = []
        if novy_nazev: updates.append("nazev = %s"); params.append(novy_nazev)
        if novy_popis: updates.append("popis = %s"); params.append(novy_popis)
        if v_stav in stavy_map: updates.append("stav = %s"); params.append(stavy_map[v_stav])

        if not updates:
            print("Žádná změna."); return

        query = f"UPDATE ukoly SET {', '.join(updates)} WHERE id = %s"
        params.append(u_id)
        
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        conn.commit()
        print("Úkol aktualizován.")
    except Exception as e:
        print(f"Chyba: {e}")

def odstranit_ukol(conn):
    """Smaže úkol podle ID."""
    u_id = input("\nZadejte ID pro smazání: ")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (u_id,))
        conn.commit()
        print(f"Smazáno (pokud ID existovalo).")
    finally:
        cursor.close()

def main():
    conn = create_db_connection()
    if not conn: return
    setup_database(conn)

    while True:
        print("\n1. Přidat | 2. Zobrazit | 3. Upravit | 4. Smazat | 5. Konec")
        v = input("Vyberte: ")
        if v == '1': pridat_ukol(conn)
        elif v == '2': zobrazit_ukoly(conn)
        elif v == '3': aktualizovat_ukol(conn)
        elif v == '4': odstranit_ukol(conn)
        elif v == '5': break
        input("\nStiskněte Enter...")

    conn.close()

if __name__ == "__main__":
    main()
