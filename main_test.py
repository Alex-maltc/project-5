import mysql.connector
from mysql.connector import Error

# --- KONFIGURACE DATABÁZE ---
DB_CONFIG = {
    'host': '127.0.0.1',  
    'database': 'Project_5_test',
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

def setup_database(conn):
    """Vytvoří tabulku 'ukoly', pokud ještě neexistuje."""
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
        # print("Tabulka 'ukoly' je připravena.") # Odkomentuj, pokud chceš vidět potvrzení při každém startu
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
        print("Chyba: Popis je povinný!")
    
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
    """
    Zobrazí pouze aktivní úkoly (Nezahájeno nebo Probíhá).
    Hotové úkoly jsou skryty.
    """
    cursor = conn.cursor()
    try:
        # SQL dotaz s filtrem: vybíráme jen to, co není hotové
        query = """
            SELECT id, nazev, popis, stav, datum_vytvoreni 
            FROM ukoly 
            WHERE stav IN ('nezahájeno', 'probíhá') 
            ORDER BY id
        """
        cursor.execute(query)
        ukoly = cursor.fetchall()

        print(f"\n{'ID':<3} | {'NÁZEV':<15} | {'STAV':<12} | {'POPIS (zkrácený)':<25}")
        print("-" * 70)
        
        if not ukoly:
            print("Seznam aktivních úkolů je prázdný.")
        else:
            for u_id, nazev, popis, stav, datum in ukoly:
                # Pokud je popis moc dlouhý, zkrátíme ho pro hezčí výpis
                kratky_popis = (popis[:22] + '..') if len(popis) > 22 else popis
                
                print(f"{u_id:<3} | {nazev:<15} | {stav:<12} | {kratky_popis:<25}")
        
        return ukoly

    except Error as e:
        print(f"Chyba při načítání úkolů: {e}")
        return []
    finally:
        cursor.close()

def aktualizovat_ukol(conn):
    """
    Změna stavu úkolu.
    Uživatel vybere ID a následně nový stav (Probíhá/Hotovo).
    """
    while True:
        # 1. Zobrazení aktuálních úkolů
        ukoly = zobrazit_ukoly(conn)
        
        if not ukoly:
            print("Není co aktualizovat.")
            return

        # 2. Výběr ID úkolu
        id_vstup = input("\nZadejte ID úkolu pro změnu stavu (nebo 'q' pro zrušení): ").strip()
        
        if id_vstup.lower() == 'q':
            return

        # Ověření, zda ID existuje v aktuálním seznamu
        platna_id = [str(u[0]) for u in ukoly] # Seznam ID z načtených úkolů
        
        if id_vstup not in platna_id:
            print(f"Chyba: Úkol s ID {id_vstup} neexistuje v seznamu. Zkuste to znovu.")
            continue 

        # 3. Výběr nového stavu
        print("\nVyberte nový stav:")
        print("1. Probíhá")
        print("2. Hotovo")
        volba_stavu = input("Vaše volba (1-2): ").strip()

        novy_stav = ""
        if volba_stavu == '1':
            novy_stav = "probíhá"
        elif volba_stavu == '2':
            novy_stav = "hotovo"
        else:
            print("Neplatná volba stavu. Aktualizace zrušena.")
            continue

        # 4. Aktualizace v databázi
        cursor = conn.cursor()
        try:
            query = "UPDATE ukoly SET stav = %s WHERE id = %s"
            cursor.execute(query, (novy_stav, id_vstup))
            conn.commit()
            print(f"\nÚkol ID {id_vstup} byl úspěšně změněn na stav: '{novy_stav}'.")
            break # Úspěšně hotovo, vyskočíme z cyklu ven
        except Error as e:
            print(f"Chyba při komunikaci s databází: {e}")
            break
        finally:
            cursor.close()

def odstranit_ukol(conn):
    """
    Uživatel vidí seznam, vybere ID a po potvrzení je úkol smazán.
    Při zadání špatného ID se dotaz opakuje.
    """
    while True:
        # 1. Zobrazení seznamu úkolů (využíváme tvou existující funkci)
        ukoly = zobrazit_ukoly(conn)
        
        if not ukoly:
            print("Seznam je prázdný, není co odstranit.")
            return

        # 2. Výběr ID úkolu
        id_vstup = input("\nZadejte ID úkolu, který chcete TRVALE SMAZAT (nebo 'q' pro zrušení): ").strip()
        
        if id_vstup.lower() == 'q':
            print("Mazání zrušeno.")
            return

        # Ověření, zda ID existuje v aktuálně načteném seznamu
        platna_id = [str(u[0]) for u in ukoly]
        
        if id_vstup not in platna_id:
            print(f"Chyba: Úkol s ID {id_vstup} neexistuje. Vyberte prosím ID ze seznamu výše.")
            continue # Zopakuje cyklus

        # 3. Potvrzení smazání (bezpečnostní krok)
        potvrzeni = input(f"Opravdu chcete úkol ID {id_vstup} trvale odstranit? (ano/ne): ").strip().lower()
        
        if potvrzeni != 'ano':
            print("Mazání přerušeno.")
            continue

        # 4. Samotné odstranění z DB
        cursor = conn.cursor()
        try:
            query = "DELETE FROM ukoly WHERE id = %s"
            cursor.execute(query, (id_vstup,))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"\nÚspěch: Úkol ID {id_vstup} byl trvale smazán z databáze.")
            break # Vše proběhlo v pořádku, ukončíme funkci
            
        except Error as e:
            print(f"Chyba při mazání z databáze: {e}")
            break
        finally:
            cursor.close()

def main():
    conn = create_db_connection()
    if not conn: return
    
    # Setup database se stará o vytvoření tabulky, pokud neexistuje
    # Není potřeba to ověřovat ručně funkcí existuje_tabulka
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