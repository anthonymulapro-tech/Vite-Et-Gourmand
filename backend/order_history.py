from .database import get_connection

def get_user_orders(utilisateur_id):
    """Récupère l'historique des commandes d'un utilisateur spécifique."""
    connection = get_connection()
    try:
        with connection.cursor(dictionary=True) as cursor:
            # On récupère les commandes de la plus récente à la plus ancienne
            sql = """
                  SELECT commande_id, \
                         reference_commande, \
                         date_commande, \
                         date_prestation, \
                         heure_livraison, \
                         (IFNULL(prix_menu, 0) + IFNULL(prix_livraison, 0)) AS total_ttc, \
                         statut_commande
                  FROM commande
                  WHERE utilisateur_id = %s
                  ORDER BY date_commande DESC \
                  """
            cursor.execute(sql, (utilisateur_id,))
            return cursor.fetchall()
    finally:
        connection.close()