from backend.database import get_connection

# Insère un nouveau message de contact dans la base de données.
def save_contact_message(nom_contact, prenom_contact, motif, description_contact, email_contact):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
                INSERT INTO message_contact (nom_contact, prenom_contact, motif, description_contact, email_contact)
                VALUES (%s, %s, %s, %s, %s) \
                """
        values = (nom_contact, prenom_contact, motif, description_contact, email_contact)
        cursor.execute(query, values)
        connection.commit()  # Très important pour valider l'écriture (INSERT)
        return True

    except Exception as e:
        print(f"Erreur lors de la sauvegarde du message : {e}")
        return False

    finally:
        cursor.close()
        connection.close()