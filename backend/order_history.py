# REPOSITORY (Historique Client)
class OrderHistoryRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_user_orders(self, user_id):
        """Récupère l'historique complet des commandes d'un utilisateur."""
        try:
            with self.db.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT commande_id, reference_commande, date_prestation, heure_livraison,
                            prix_menu, prix_livraison, pret_materiel,
                            (IFNULL(prix_menu, 0) + IFNULL(prix_livraison, 0)) AS total_ttc,
                            statut_commande, adresse_livraison, ville_livraison, code_postal_livraison
                    FROM commande 
                    WHERE utilisateur_id = %s
                    ORDER BY commande_id DESC
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur get_user_orders : {e}")
            return []

    def get_order_details(self, commande_id, user_id):
        """Récupère les menus d'une commande et vérifie si un avis existe pour CETTE commande."""
        try:
            with self.db.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT m.menu_id, m.titre_menu, cm.quantite, m.prix_par_personne,
                           (SELECT COUNT(*) FROM avis a WHERE a.menu_id = m.menu_id AND a.commande_id = %s) AS a_deja_note
                    FROM commande_menu cm
                    JOIN menu m ON cm.menu_id = m.menu_id
                    WHERE cm.commande_id = %s
                """
                # On passe commande_id deux fois (une pour la sous-requête, une pour le WHERE principal)
                cursor.execute(sql, (commande_id, commande_id))
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur get_order_details : {e}")
            return []

    def cancel_client_order(self, commande_id, user_id):
        """Permet au client d'annuler sa commande UNIQUEMENT si elle est 'En attente'."""
        try:
            with self.db.cursor() as cursor:
                sql = """UPDATE commande 
                         SET statut_commande = 'Annulé' 
                         WHERE commande_id = %s AND utilisateur_id = %s AND statut_commande = 'En attente'"""
                cursor.execute(sql, (commande_id, user_id))
                self.db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de l'annulation client : {e}")
            return False

    def add_client_review(self, user_id, menu_id, commande_id, note, commentaire):
        """Ajoute un avis client lié à une commande précise."""
        try:
            with self.db.cursor() as cursor:
                # On vérifie le doublon sur la commande précise
                check_sql = "SELECT COUNT(*) FROM avis WHERE commande_id = %s AND menu_id = %s"
                cursor.execute(check_sql, (commande_id, menu_id))
                if cursor.fetchone()[0] > 0:
                    return False

                # On insère avec le commande_id
                insert_sql = """INSERT INTO avis (utilisateur_id, menu_id, commande_id, note, commentaire)
                                VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(insert_sql, (user_id, menu_id, commande_id, note, commentaire))
                self.db.commit()
                return True
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'avis : {e}")
            return False