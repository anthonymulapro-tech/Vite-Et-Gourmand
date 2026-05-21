from backend.database import get_connection


# Récupère la liste des horaires de la base de données et formate les heures (HH:MM).
def get_schedule():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
                SELECT horaire_id, \
                       jour, \
                       heure_midi_ouverture, \
                       heure_midi_fermeture, \
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


def update_day_schedule(horaire_id, midi_ouvrir, midi_fermer, soir_ouvrir, soir_fermer, est_ouvert_val):
    """Met à jour les horaires d'un jour précis. Gère les valeurs fermées (NULL)."""
    db = get_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()

        # Si le jour est marqué fermé ou vide, on insère proprement NULL en BDD
        m_open = midi_ouvrir if midi_ouvrir and est_ouvert_val == 1 else None
        m_close = midi_fermer if midi_fermer and est_ouvert_val == 1 else None
        s_open = soir_ouvrir if soir_ouvrir and est_ouvert_val == 1 else None
        s_close = soir_fermer if soir_fermer and est_ouvert_val == 1 else None

        sql = """
              UPDATE horaire
              SET heure_midi_ouverture = %s,
                  heure_midi_fermeture = %s,
                  heure_soir_ouverture = %s,
                  heure_soir_fermeture = %s,
                  est_ouvert           = %s
              WHERE horaire_id = %s \
              """
        cursor.execute(sql, (m_open, m_close, s_open, s_close, est_ouvert_val, horaire_id))
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur SQL lors de la modification de l'horaire #{horaire_id} : {e}")
        return False
    finally:
        db.close()