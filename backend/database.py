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

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        conn.close()