import mysql.connector
from mysql.connector import Error

# --- KONFIGURACE DATABÁZE ---
DB_CONFIG = {
    'host': '127.0.0.1',  
    'database': 'Project_5',
    'user': 'root',      
    'password': '2020' 
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
    
def main():
    conn = create_db_connection()
    if not conn: return
    
    # Ověříme, zda už máme tabulku připravenou
    if existuje_tabulka(conn, "ukoly"):
        print("Tabulka 'ukoly' nalezena, můžeme pracovat.")
    else:
        print("Tabulka nenalezena, spouštím instalaci...")
        setup_database(conn)

def setup_database(conn):
    """Vytvoří tabulku 'ukoly' s rozšířenými sloupci a NOT NULL omezením."""
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
        print("Tabulka 'ukoly' je připravena (včetně NOT NULL pro popis).")
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")
    finally:
        cursor.close()

def pridat_ukol(conn):
    """Vloží nový úkol s povinným názvem a popisem."""
    print("\n--- Přidání nového úkolu ---")
    
    # Validace: Název nesmí být prázdný
    while True:
        nazev = input("Název: ").strip()
        if nazev:
            break
        print("Chyba: Název je povinný!")

    # Validace: Popis nesmí být prázdný
    while True:
        popis = input("Popis: ").strip()
        if popis:
            break
        print("Chyba: Popis je povinný (nastaveno NOT NULL)!")
    
    print("Vyberte stav: 1. nezahájeno (default), 2. probíhá, 3. hotovo")
    volba_stavu = input("Volba (1-3): ")
    stavy_map = {'1': 'nezahájeno', '2': 'probíhá', '3': 'hotovo'}
    stav = stavy_map.get(volba_stavu, 'nezahájeno')

    query = "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    try:
        cursor.execute(query, (nazev, popis, stav))
        conn.commit()
        print(f"Úkol '{nazev}' byl úspěšně přidán.")
    except Error as e:
        print(f"Chyba v databázi: {e}")
    finally:
        cursor.close()

def zobrazit_ukoly(conn):
    """Načte a přehledně zobrazí všechny úkoly."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nazev, popis, stav, datum_vytvoreni FROM ukoly")
        ukoly = cursor.fetchall()

        print(f"\n{'ID':<3} | {'NÁZEV':<15} | {'STAV':<12} | {'VYTVOŘENO':<19}")
        print("-" * 65)
        
        if not ukoly:
            print("Seznam úkolů je prázdný.")
        else:
            for u_id, nazev, popis, stav, datum in ukoly:
                cas = datum.strftime("%d.%m.%Y %H:%M")
                print(f"{u_id:<3} | {nazev:<15} | {stav:<12} | {cas}")
        return ukoly
    except Error as e:
        print(f"Chyba při načítání: {e}")
    finally:
        cursor.close()

def aktualizovat_ukol(conn):
    """Umožní aktualizaci polí úkolu."""
    ukoly = zobrazit_ukoly(conn)
    if not ukoly: return

    try:
        u_id = int(input("\nZadejte ID úkolu pro změnu: "))
        novy_nazev = input("Nový název (Enter pro přeskočení): ").strip()
        novy_popis = input("Nový popis (Enter pro přeskočení): ").strip()
        print("Nový stav: 1. nezahájeno, 2. probíhá, 3. hotovo (Enter pro přeskočení)")
        v_stav = input("Volba: ")
        
        stavy_map = {'1': 'nezahájeno', '2': 'probíhá', '3': 'hotovo'}
        updates = []
        params = []

        if novy_nazev: updates.append("nazev = %s"); params.append(novy_nazev)
        if novy_popis: updates.append("popis = %s"); params.append(novy_popis)
        if v_stav in stavy_map: updates.append("stav = %s"); params.append(stavy_map[v_stav])

        if not updates:
            print("Nebyla provedena žádná změna."); return

        query = f"UPDATE ukoly SET {', '.join(updates)} WHERE id = %s"
        params.append(u_id)
        
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        conn.commit()
        print("Úkol byl úspěšně aktualizován.")
    except Exception as e:
        print(f"Došlo k chybě: {e}")

def odstranit_ukol(conn):
    """Smaže úkol z databáze podle ID."""
    u_id = input("\nZadejte ID úkolu, který chcete smazat: ")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (u_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Úkol s ID {u_id} byl smazán.")
        else:
            print("Úkol s tímto ID nebyl nalezen.")
    finally:
        cursor.close()

def main():
    conn = create_db_connection()
    if not conn: return
    setup_database(conn)

    while True:
        print("\n--- MENU ---")
        print("1. Přidat | 2. Zobrazit | 3. Upravit | 4. Smazat | 5. Konec")
        v = input("Vyberte možnost: ")
        
        if v == '1': pridat_ukol(conn)
        elif v == '2': zobrazit_ukoly(conn)
        elif v == '3': aktualizovat_ukol(conn)
        elif v == '4': odstranit_ukol(conn)
        elif v == '5': 
            print("Ukončuji program...")
            break
        else:
            print("Neplatná volba!")
        
        input("\nStiskněte Enter pro návrat do menu...")

    if conn.is_connected():
        conn.close()

if __name__ == "__main__":
    main()