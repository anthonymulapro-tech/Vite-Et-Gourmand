import mysql.connector
import os
from dotenv import load_dotenv

# Chargement du fichier .env
load_dotenv()

# Connexion à la BDD
def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            print("Connexion à la base de données réussie !")
            return connection
    except mysql.connector.Error as err:
        print(f"Erreur : {err}")
        return None

# Initialisation des tables via le fichier SQL
def init_database():
    connection = get_connection()
    if connection is None:
        return

    try:
        cursor = connection.cursor()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_file_path = os.path.join(base_dir, 'sql', '01_create_tables.sql')

        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        # Séparation du script en plusieurs commandes grâce au ";"
        sql_commands = sql_script.split(';')
        print("Création des tables en cours...")

        for command in sql_commands:
            # Nettoyage des espaces et vérification que la commande ne soit pas vide
            clean_command = command.strip()
            if clean_command:
                cursor.execute(clean_command)
        connection.commit()
        print("Les tables ont été créées avec succès !")

    except Exception as e:
        print(f"Erreur lors de la création : {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Zone de test
if __name__ == "__main__":
    print("--- Test de la base de données ---")
    # test de la connexion
    conn = get_connection()
    if conn and conn.is_connected():
        print("Connexion basique réussie !")
        conn.close()

        # Si la connexion marche, lancement de l'initialisation
        print("\n--- Lancement de l'initialisation ---")
        init_database()