from .database import get_connection

def get_user_orders(user_id):
    connection = get_connection()
    try:
        with connection.cursor(dictionary=True) as cursor:
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
    finally:
        connection.close()

def get_order_details(commande_id):
    """Récupère la liste des menus d'une commande précise avec quantités et prix."""
    connection = get_connection() # Utilise la fonction de database.py
    try:
        with connection.cursor(dictionary=True) as cursor:
            sql = """
                SELECT m.menu_id, m.titre_menu, cm.quantite, m.prix_par_personne
                FROM commande_menu cm
                JOIN menu m ON cm.menu_id = m.menu_id
                WHERE cm.commande_id = %s
            """
            cursor.execute(sql, (commande_id,))
            return cursor.fetchall()
    finally:
        connection.close()

def cancel_client_order(commande_id, user_id):
    """Permet au client d'annuler sa commande UNIQUEMENT si elle est 'En attente'."""
    db = get_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        # On utilise statut_commande comme dans la BDD
        sql = """UPDATE commande 
                 SET statut_commande = 'Annulé' 
                 WHERE commande_id = %s AND utilisateur_id = %s AND statut_commande = 'En attente'"""
        cursor.execute(sql, (commande_id, user_id))
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur lors de l'annulation client : {e}")
        return False
    finally:
        db.close()

def add_client_review(user_id, menu_id, note, commentaire):
    """Ajoute un avis client en BDD pour un menu spécifique."""
    db = get_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        # statut_avis prendra la valeur 'En attente' par défaut grâce au DEFAULT de la BDD
        sql = """INSERT INTO avis (utilisateur_id, menu_id, note, commentaire) 
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (user_id, menu_id, note, commentaire))
        db.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'avis : {e}")
        return False
    finally:
        db.close()