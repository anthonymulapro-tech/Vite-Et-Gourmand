import mysql.connector
import os
from dotenv import load_dotenv

# Détermination du chemin absolu vers la racine du projet pour trouver le .env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, '.env')

# Chargement robuste du fichier .env
load_dotenv(dotenv_path)


# Connexion à la BDD
def get_connection(connect_to_db=True):
    try:
        db_port = int(os.getenv("DB_PORT", 3306))

        # Paramètres de connexion de base
        conn_params = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "port": db_port
        }

        # Sélection la base de données seulement si connect_to_db est True
        if connect_to_db:
            conn_params["database"] = os.getenv("DB_NAME")

        connection = mysql.connector.connect(**conn_params)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        # Affichage erreur
        print(f"Erreur de connexion MySQL : {err}")
        return None


# Initialisation des tables via le fichier SQL
def init_database():
    # Connexion sans base de données au départ pour pouvoir la créer
    connection = get_connection(connect_to_db=False)
    if connection is None:
        print("Impossible de se connecter au serveur MySQL pour l'initialisation.")
        return

    try:
        cursor = connection.cursor()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_file_path = os.path.join(base_dir, 'sql', '01_create_tables.sql')

        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        # Séparation du script en plusieurs commandes grâce au ";"
        sql_commands = sql_script.split(';')
        print("Création de la base de données et des tables en cours...")

        for command in sql_commands:
            clean_command = command.strip()
            if clean_command:
                cursor.execute(clean_command)
        connection.commit()
        print("La base de données et les tables ont été créées avec succès !")

    except Exception as e:
        print(f"Erreur lors de la création : {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def insert_initial_data():
    """Remplit la base de données (02_insert_data.sql)."""
    # La base de données a été créée
    connection = get_connection(connect_to_db=True)
    if connection is None:
        print("Impossible de se connecter à la base de données pour insérer les données.")
        return

    try:
        cursor = connection.cursor()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_file_path = os.path.join(base_dir, 'sql', '02_insert_data.sql')

        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        sql_commands = sql_script.split(';')
        print("Insertion des données de test...")

        count = 0
        for command in sql_commands:
            clean_command = command.strip()
            if clean_command:
                cursor.execute(clean_command)
                count += 1

        connection.commit()
        print(f"Succès ! {count} blocs de données insérés.")

    except Exception as e:
        connection.rollback()
        print(f"Erreur lors de l'insertion : {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# Zone de test
if __name__ == "__main__":
    print("--- INITIALISATION VITE & GOURMAND ---")

    # 1. Test de connexion rapide au serveur MySQL (sans BDD au cas où elle n'existe pas)
    test_conn = get_connection(connect_to_db=False)
    if test_conn:
        print("Connexion au serveur MySQL : OK")
        test_conn.close()

        # 2. Lancement de la structure (Crée la base de données et les tables)
        init_database()

        # 3. Lancement des données (Remplit la base de données)
        insert_initial_data()

        print("\n--- CONFIGURATION TERMINÉE ---")
    else:
        print("Impossible de démarrer : Vérifiez votre serveur MySQL (Laragon).")