from .database import get_connection

def get_all_orders_for_employee():
    """Récupère toutes les commandes de la base avec les coordonnées du client, triées par urgence de prestation."""
    connection = get_connection()
    if not connection:
        return []
    try:
        with connection.cursor(dictionary=True) as cursor:
            sql = """
                SELECT c.commande_id, c.reference_commande, c.date_commande, 
                       c.date_prestation, c.heure_livraison, c.prix_menu, c.prix_livraison,
                       (IFNULL(c.prix_menu, 0) + IFNULL(c.prix_livraison, 0)) AS total_ttc,
                       c.statut_commande, c.pret_materiel, c.restitution_materiel,
                       c.adresse_livraison, c.code_postal_livraison, c.ville_livraison,
                       u.prenom, u.nom, u.telephone
                FROM commande c
                JOIN utilisateur u ON c.utilisateur_id = u.utilisateur_id
                ORDER BY c.date_prestation DESC, c.date_commande DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Erreur lors de la récupération des commandes employé : {e}")
        return []
    finally:
        connection.close()

def update_order_status_and_material(commande_id, nouveau_statut, restitution_materiel_val):
    """Met à jour le statut de la commande et le suivi de la restitution du matériel."""
    db = get_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        sql = """
            UPDATE commande 
            SET statut_commande = %s, restitution_materiel = %s 
            WHERE commande_id = %s
        """
        cursor.execute(sql, (nouveau_statut, restitution_materiel_val, commande_id))
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la commande #{commande_id} : {e}")
        return False
    finally:
        db.close()