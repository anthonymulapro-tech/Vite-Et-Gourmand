from backend.database import get_connection

#Récupère tous les avis approuvés avec le prénom et le nom de l'utilisateur associé.
def get_validated_reviews():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Ajout de ORDER BY pour la nouveauté et LIMIT 6 pour restreindre l'affichage
        query = """
                SELECT a.commentaire, a.note, u.prenom, u.nom
                FROM avis a
                         INNER JOIN utilisateur u ON a.utilisateur_id = u.utilisateur_id
                WHERE a.statut_avis = 'Validé'
                ORDER BY a.date_avis DESC
                LIMIT 6
                """
        cursor.execute(query)
        reviews_raw = cursor.fetchall()

        reviews = []
        for row in reviews_raw:
            reviews.append({
                'commentaire': row['commentaire'],
                'note': row['note'],
                'utilisateur': {
                    'prenom': row['prenom'],
                    'nom': row['nom']
                }
            })
        return reviews

    finally:
        cursor.close()
        connection.close()

