from backend.database import get_connection

# Récupère tous les menus de la base de données avec leurs relations (thèmes, régimes, photos) formatés pour Jinja2.
def get_all_menus():
    connection = get_connection()
    # dictionary=True permet de récupérer les lignes sous forme de dictionnaires Python
    cursor = connection.cursor(dictionary=True)

    try:
        # Récupération des menus avec leurs thèmes et régimes (Jointures LEFT JOIN)
        query = """
                SELECT m.*, t.nom_theme, r.nom_regime
                FROM menu m
                         LEFT JOIN theme t ON m.theme_id = t.theme_id
                         LEFT JOIN regime r ON m.regime_id = r.regime_id \
                """
        cursor.execute(query)
        menus_raw = cursor.fetchall()

        menus = []
        for row in menus_raw:
            menu_id = row['menu_id']

            # Récupération des photos liées à ce menu spécifique
            photo_query = """
                          SELECT url_photo, alt_text
                          FROM photo_menu
                          WHERE menu_id = %s
                          ORDER BY ordre_affichage \
                          """
            cursor.execute(photo_query, (menu_id,))
            photos = cursor.fetchall()

            # Structuration en dictionnaire imbriqué
            menu_dict = {
                'menu_id': row['menu_id'],
                'titre_menu': row['titre_menu'],
                'description_menu': row['description_menu'],
                'nombre_personne_min': row['nombre_personne_min'],
                'prix_par_personne': row['prix_par_personne'],
                'conditions': row['conditions'],
                'quantite_restante': row['quantite_restante'],
                'seuil_reduction': row['seuil_reduction'],
                'pourcentage_reduction': row['pourcentage_reduction'],
                'theme': {'nom_theme': row['nom_theme']} if row['nom_theme'] else None,
                'regime': {'nom_regime': row['nom_regime']} if row['nom_regime'] else None,
                'photos': photos
            }
            menus.append(menu_dict)

        return menus

    finally:
        cursor.close()
        connection.close()

