from backend.database import get_connection

# Récupère la liste des horaires de la base de données et formate les heures (HH:MM).
def get_schedule():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
                SELECT jour, \
                       heure_midi_ouverture, \
                       heure_midi_fermeture,
                       heure_soir_ouverture, \
                       heure_soir_fermeture, \
                       est_ouvert
                FROM horaire \
                """
        cursor.execute(query)
        horaires = cursor.fetchall()

        # Nettoyage du format d'heure timedelta de mysql-connector (HH:MM:SS -> HH:MM)
        for h in horaires:
            if h['heure_midi_ouverture']:
                h['heure_midi_ouverture'] = str(h['heure_midi_ouverture'])[:-3]
            if h['heure_midi_fermeture']:
                h['heure_midi_fermeture'] = str(h['heure_midi_fermeture'])[:-3]
            if h['heure_soir_ouverture']:
                h['heure_soir_ouverture'] = str(h['heure_soir_ouverture'])[:-3]
            if h['heure_soir_fermeture']:
                h['heure_soir_fermeture'] = str(h['heure_soir_fermeture'])[:-3]

        return horaires

    finally:
        cursor.close()
        connection.close()