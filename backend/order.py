import uuid
from datetime import datetime
from backend.database import get_connection


def create_order(utilisateur_id, cart_items, prix_menu, prix_livraison, pret_materiel, adresse_livraison,
                 ville_livraison, code_postal_livraison, date_prestation, heure_livraison):

    conn = get_connection()
    if not conn:
        return False, "Erreur de connexion à la base de données."

    try:
        cursor = conn.cursor()
        now = datetime.now()

        # 1. Génération de la référence
        cursor.execute("SELECT COUNT(*) FROM commande WHERE DATE(date_commande) = %s", (now.date(),))
        numero_seq = (cursor.fetchone()[0] % 99) + 1
        ref_commande = f"{str(uuid.uuid4())[:4].upper()}-{now.strftime('%d%m%Y-%H%M')}-{numero_seq:03d}"

        # 2. Préparation des données spécifiques
        nombre_personne = sum(item['quantity'] for item in cart_items)
        pret_materiel_bool = 1 if pret_materiel == 'yes' else 0

        # 3. Insertion de la commande (Les variables et le SQL ont maintenant les mêmes noms)
        sql_commande = """
                       INSERT INTO commande (reference_commande, utilisateur_id, date_prestation, heure_livraison, \
                                             prix_menu, nombre_personne, prix_livraison, ville_livraison, \
                                             adresse_livraison, code_postal_livraison, statut_commande, pret_materiel)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
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

        # Préparation des lignes pour executemany avec les données fusionnées
        lignes_a_inserer = [(commande_id, m_id, qte) for m_id, qte in panier_fusionne.items()]

        cursor.executemany(sql_ligne, lignes_a_inserer)

        conn.commit()
        return True, ref_commande

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erreur lors de la création de la commande : {e}")
        return False, f"Erreur technique : {str(e)}"

    finally:
        if conn:
            cursor.close()
            conn.close()