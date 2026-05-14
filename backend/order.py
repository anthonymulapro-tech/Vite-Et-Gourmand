import uuid
from datetime import datetime, timedelta
from backend.database import get_connection


def create_order(user_id, cart_items, total_menus, total_delivery, delivery_zone, need_material, adresse_livraison, ville_livraison, code_postal_livraison):
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

        # 2. Insertion de la commande (Variables simplifiées)
        sql_commande = """
                       INSERT INTO commande
                       (reference_commande, date_prestation, heure_livraison, prix_menu, nombre_personne,
                        prix_livraison, ville_livraison, statut_commande, pret_materiel, adresse_livraison, ville_livraison, code_postal_livraison, utilisateur_id)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                       """
        cursor.execute(sql_commande, (
            ref_commande,
            now + timedelta(days=2),
            "12:00",
            total_menus,
            sum(item['quantity'] for item in cart_items),
            total_delivery,
            "Bordeaux Centre" if delivery_zone == "bordeaux" else "Hors Bordeaux",
            'En attente',
            (need_material == 'yes'),
            user_id
        ))

        commande_id = cursor.lastrowid

        # 3. Insertion groupée des lignes du panier
        sql_ligne = "INSERT INTO commande_menu (commande_id, menu_id, quantite) VALUES (%s, %s, %s)"
        # liste de tuples contenant les infos de chaque menu
        lignes_a_inserer = [(commande_id, item['id_menu'], item['quantity']) for item in cart_items]

        # executemany fait tout le travail en une seule requête SQL
        cursor.executemany(sql_ligne, lignes_a_inserer)

        conn.commit()
        return True, ref_commande

    except Exception as e:
        conn.rollback()
        print(f"Erreur transactionnelle : {e}")
        return False, "Une erreur a empêché la validation de la commande."

    finally:
        cursor.close()
        conn.close()