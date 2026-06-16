# Insère un nouveau message de contact dans la base de données.
class ContactRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def save_contact_message(self, nom_contact, prenom_contact, motif, description_contact, email_contact):
        cursor = self.db.cursor()

        try:
            query = """
                    INSERT INTO message_contact (nom_contact, prenom_contact, motif, description_contact, email_contact)
                    VALUES (%s, %s, %s, %s, %s)
                    """
            values = (nom_contact, prenom_contact, motif, description_contact, email_contact)
            cursor.execute(query, values)
            # Validation de l'écriture
            self.db.commit()
            return True

        except Exception as e:
            print(f"Erreur lors de la sauvegarde du message : {e}")
            return False

        finally:
            cursor.close()