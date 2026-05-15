from .database import get_connection

def get_user_orders(user_id):
    connection = get_connection()
    try:
        with connection.cursor(dictionary=True) as cursor:
            # AJOUTE LES COLONNES D'ADRESSE ICI 👇
            sql = """
                SELECT commande_id, reference_commande, date_prestation, heure_livraison,
                        (IFNULL(prix_menu, 0) + IFNULL(prix_livraison, 0)) AS total_ttc,
                        statut_commande, adresse_livraison, ville_livraison, code_postal_livraison
                FROM commande 
                WHERE utilisateur_id = %s
                ORDER BY commande_id DESC
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
    finally:
        connection.close()

def get_order_details(commande_id):
    """Récupère la liste des menus d'une commande précise avec quantités et prix."""
    connection = get_connection() # Utilise ta fonction de database.py
    try:
        with connection.cursor(dictionary=True) as cursor:
            sql = """
                SELECT m.titre_menu, cm.quantite, m.prix_par_personne
                FROM commande_menu cm
                JOIN menu m ON cm.menu_id = m.menu_id
                WHERE cm.commande_id = %s
            """
            cursor.execute(sql, (commande_id,))
            return cursor.fetchall()
    finally:
        connection.close()