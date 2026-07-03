import uuid
from datetime import datetime


# REPOSITORY (Les Commandes)
class OrderRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_order(self, utilisateur_id, cart_items, prix_menu, prix_livraison, pret_materiel, adresse_livraison,
                     ville_livraison, code_postal_livraison, date_prestation, heure_livraison):
        """
        Crée une commande en base de données et insère les lignes de menus associées.
        Gère la transaction de manière sécurisée (Commit/Rollback).
        """
        if not self.db:
            return False, "Erreur de connexion à la base de données."

        cursor = None
        try:
            cursor = self.db.cursor()
            now = datetime.now()

            # 1. Génération de la référence unique
            cursor.execute("SELECT COUNT(*) FROM commande WHERE DATE(date_commande) = %s", (now.date(),))
            numero_seq = (cursor.fetchone()[0] % 99) + 1
            ref_commande = f"{str(uuid.uuid4())[:4].upper()}-{now.strftime('%d%m%Y-%H%M')}-{numero_seq:03d}"

            # 2. Préparation des données spécifiques
            nombre_personne = sum(item['quantity'] for item in cart_items)
            pret_materiel_bool = 1 if pret_materiel == 'yes' else 0

            # 3. Insertion de la commande principale
            sql_commande = """
                           INSERT INTO commande (reference_commande, utilisateur_id, date_prestation, heure_livraison,
                                                 prix_menu, nombre_personne, prix_livraison, ville_livraison,
                                                 adresse_livraison, code_postal_livraison, statut_commande, pret_materiel)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """

            valeurs_commande = (
                ref_commande,
                utilisateur_id,
                date_prestation,
                heure_livraison,
                prix_menu,
                nombre_personne,
                prix_livraison,
                ville_livraison,
                adresse_livraison,
                code_postal_livraison,
                'En attente',
                pret_materiel_bool
            )

            cursor.execute(sql_commande, valeurs_commande)
            commande_id = cursor.lastrowid

            # 4. Insertion des lignes de menus (Table commande_menu)
            sql_ligne = "INSERT INTO commande_menu (commande_id, menu_id, quantite) VALUES (%s, %s, %s)"

            # Fusion des quantités si un menu est présent plusieurs fois dans le panier
            panier_fusionne = {}
            for item in cart_items:
                m_id = item['id_menu']
                if m_id in panier_fusionne:
                    panier_fusionne[m_id] += item['quantity']
                else:
                    panier_fusionne[m_id] = item['quantity']

            # Préparation des lignes pour executemany
            lignes_a_inserer = [(commande_id, m_id, qte) for m_id, qte in panier_fusionne.items()]
            cursor.executemany(sql_ligne, lignes_a_inserer)

            # Si tout s'est bien passé, on valide la transaction globale
            self.db.commit()
            return True, ref_commande

        except Exception as e:
            # En cas d'erreur sur l'une des étapes, annulation de l'ensemble pour éviter les données fantômes
            if self.db:
                self.db.rollback()
            print(f"Erreur lors de la création de la commande : {e}")
            return False, f"Erreur technique : {str(e)}"

        finally:
            if cursor:
                cursor.close()
            # La connexion reste ouverte, c'est app.py qui la fermera à la fin de la requête HTTP