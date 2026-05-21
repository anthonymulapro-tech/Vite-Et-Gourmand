from backend.database import get_connection

# Récupère tous les menus de la base de données avec leurs relations (thèmes, régimes, photos) formatés pour Jinja2.
def get_all_menus():
    connection = get_connection()
    # dictionary=True permet de récupérer les lignes sous forme de dictionnaires Python
    cursor = connection.cursor(dictionary=True)

    try:
        # Récupération des menus avec leurs thèmes ,régimes et allergènes (Jointures LEFT JOIN)
        query = """
                SELECT m.*, t.nom_theme, r.nom_regime,
                       GROUP_CONCAT(DISTINCT a.nom_allergene) as liste_allergenes
                FROM menu m
                LEFT JOIN theme t ON m.theme_id = t.theme_id
                LEFT JOIN regime r ON m.regime_id = r.regime_id
                LEFT JOIN menu_plat mp ON m.menu_id = mp.menu_id
                LEFT JOIN plat_allergene pa ON mp.plat_id = pa.plat_id
                LEFT JOIN allergene a ON pa.allergene_id = a.allergene_id
                GROUP BY m.menu_id
                """
        cursor.execute(query)
        menus_raw = cursor.fetchall()

        menus = []
        for row in menus_raw:
            menu_id = row['menu_id']
            allergenes_str = row['liste_allergenes']
            liste_allergenes = [a.lower().strip() for a in allergenes_str.split(',')] if allergenes_str else []

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
                'allergenes': liste_allergenes,
                'photos': photos
            }
            menus.append(menu_dict)

        return menus

    finally:
        cursor.close()
        connection.close()

