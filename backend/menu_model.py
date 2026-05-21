from mysql.connector import Error

def get_menu_details(db_connection, menu_id):
    if db_connection is None:
        return None

    try:
        cursor = db_connection.cursor(dictionary=True)

        # 1. Infos générales du menu
        query_menu = """
            SELECT m.*, t.nom_theme, r.nom_regime
            FROM menu m
            LEFT JOIN theme t ON m.theme_id = t.theme_id
            LEFT JOIN regime r ON m.regime_id = r.regime_id
            WHERE m.menu_id = %s
        """
        cursor.execute(query_menu, (menu_id,))
        menu = cursor.fetchone()

        if not menu:
            return None

        # 2. Récupération des plats associés
        query_plats = """
                      SELECT p.*,
                             (SELECT GROUP_CONCAT(a.nom_allergene SEPARATOR ', ')
                              FROM allergene a
                                       JOIN plat_allergene pa ON a.allergene_id = pa.allergene_id
                              WHERE pa.plat_id = p.plat_id) as allergenes
                      FROM plat p
                               JOIN menu_plat mp ON p.plat_id = mp.plat_id
                      WHERE mp.menu_id = %s
                      ORDER BY mp.ordre_affichage_plat ASC \
                      """
        cursor.execute(query_plats, (menu_id,))
        plats = cursor.fetchall()

        # Organisation par catégories pour le template Jinja
        menu['entrees'] = [p for p in plats if p['categorie'] == 'Entrée']
        menu['plats_principaux'] = [p for p in plats if p['categorie'] == 'Plat']
        menu['desserts'] = [p for p in plats if p['categorie'] == 'Dessert']

        return menu

    except Error as e:
        print(f"Erreur SQL : {e}")
        return None
    finally:
        if cursor:
            cursor.close()