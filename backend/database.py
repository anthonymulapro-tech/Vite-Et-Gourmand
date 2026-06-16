import mysql.connector
import os
from dotenv import load_dotenv

# Détermination du chemin absolu vers la racine du projet pour trouver le .env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)


# ==========================================
# GESTIONNAIRE DE BASE DE DONNÉES (POO)
# ==========================================
class DatabaseManager:

    @staticmethod
    def get_connection(connect_to_db=True):
        """Établit et retourne une connexion à la base de données."""
        try:
            db_port = int(os.getenv("DB_PORT", 3306))
            db_host = os.getenv("DB_HOST", "").strip()
            db_user = os.getenv("DB_USER", "").strip()
            db_password = os.getenv("DB_PASSWORD", "").strip()
            db_name = os.getenv("DB_NAME", "").strip()

            if not db_host:
                print("Erreur critique : DB_HOST est introuvable ou vide.")
                return None

            conn_params = {
                "host": db_host,
                "user": db_user,
                "password": db_password,
                "port": db_port
            }

            # Aiven exige une connexion sécurisée (SSL)
            if "aivencloud" in db_host:
                conn_params["ssl_disabled"] = False

            if connect_to_db and db_name:
                conn_params["database"] = db_name

            connection = mysql.connector.connect(**conn_params)
            if connection.is_connected():
                return connection

        except mysql.connector.Error as err:
            print(f"Erreur de connexion MySQL : {err}")
            return None

    @classmethod
    def init_database(cls):
        """Initialise les tables via le fichier SQL."""
        connection = cls.get_connection(connect_to_db=False)
        if connection is None:
            print("Impossible de se connecter au serveur MySQL pour l'initialisation.")
            return

        try:
            cursor = connection.cursor()
            sql_file_path = os.path.join(base_dir, 'sql', '01_create_tables.sql')

            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_script = file.read()

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

    @classmethod
    def insert_initial_data(cls):
        """Remplit la base de données avec le jeu de données initial."""
        connection = cls.get_connection(connect_to_db=True)
        if connection is None:
            print("Impossible de se connecter à la base de données pour insérer les données.")
            return

        try:
            cursor = connection.cursor()
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


# ==========================================
# FAÇADE (Rétrocompatibilité)
# ==========================================
# Ces fonctions permettent à ton app.py et tes autres fichiers de
# continuer à fonctionner sans changer leurs lignes d'importation.
def get_connection(connect_to_db=True):
    return DatabaseManager.get_connection(connect_to_db)


def init_database():
    DatabaseManager.init_database()


def insert_initial_data():
    DatabaseManager.insert_initial_data()


# ==========================================
# ZONE DE TEST (Lancement direct)
# ==========================================
if __name__ == "__main__":
    print("--- INITIALISATION VITE & GOURMAND ---")

    test_conn = DatabaseManager.get_connection(connect_to_db=False)
    if test_conn:
        print("Connexion au serveur MySQL : OK")
        test_conn.close()

        DatabaseManager.init_database()
        DatabaseManager.insert_initial_data()

        print("\n--- CONFIGURATION TERMINÉE ---")
    else:
        print("Impossible de démarrer : Vérifiez votre serveur MySQL.")