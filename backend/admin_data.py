import os
from pymongo import MongoClient
from backend.database import get_connection
from datetime import datetime, timedelta


def get_mongo_db():
    """Établit la connexion avec le cluster MongoDB local."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/vite_et_gourmand_stats")
    client = MongoClient(mongo_uri)
    # Retourne la base de données spécifique (elle sera créée automatiquement si elle n'existe pas)
    return client.get_database()


def sync_mysql_to_mongo():
    """
    Processus ETL :
    Extrait les ventes validées de MySQL, les nettoie,
    et les insère dans la collection NoSQL 'ventes_menus'.
    """
    mysql_conn = get_connection()
    if not mysql_conn:
        return False, "Erreur de connexion MySQL"

    db = get_mongo_db()
    collection = db.ventes_menus

    try:
        with mysql_conn.cursor(dictionary=True) as cursor:
            # Extraction (Extract) : On joint nos 3 tables pour avoir des données lisibles
            sql = """
                  SELECT c.reference_commande, \
                         c.date_commande, \
                         m.titre_menu, \
                         cm.quantite, \
                         (cm.quantite * m.prix_par_personne) AS chiffre_affaires_brut
                  FROM commande_menu cm
                           JOIN commande c ON cm.commande_id = c.commande_id
                           JOIN menu m ON cm.menu_id = m.menu_id
                  WHERE c.statut_commande != 'Annulé' \
                  """
            cursor.execute(sql)
            lignes_ventes = cursor.fetchall()

        if lignes_ventes:
            # Transformation : On convertit le Decimal MySQL en Float pour MongoDB
            for ligne in lignes_ventes:
                if ligne['chiffre_affaires_brut']:
                    ligne['chiffre_affaires_brut'] = float(ligne['chiffre_affaires_brut'])

            # Load : On vide l'entrepôt et on insère les données fraîches (Full Sync)
            collection.delete_many({})
            collection.insert_many(lignes_ventes)

        return True, f"Synchronisation réussie : {len(lignes_ventes)} lignes de ventes importées."

    except Exception as e:
        print(f"Erreur lors de la synchro ETL : {e}")
        return False, "Erreur technique lors de la migration vers MongoDB."
    finally:
        mysql_conn.close()


def get_nosql_data():
    """
    Utilise les pipelines d'agrégation natifs de MongoDB ($group, $sum, $sort)
    pour formater les données pour nos graphiques.
    """
    db = get_mongo_db()
    collection = db.ventes_menus

    # Agrégation 1 : Top des ventes (Quantité)
    pipeline_quantite = [
        {"$group": {"_id": "$titre_menu", "total_vendus": {"$sum": "$quantite"}}},
        {"$sort": {"total_vendus": -1}}
    ]

    # Agrégation 2 : Chiffre d'Affaires par menu
    pipeline_ca = [
        {"$group": {"_id": "$titre_menu", "ca_total": {"$sum": "$chiffre_affaires_brut"}}},
        {"$sort": {"ca_total": -1}}
    ]

    data_quantite = list(collection.aggregate(pipeline_quantite))
    data_ca = list(collection.aggregate(pipeline_ca))

    # Formatage final sous forme de listes pour Chart.js (Front-End)
    return {
        "quantite": {
            "labels": [item['_id'] for item in data_quantite],
            "data": [item['total_vendus'] for item in data_quantite]
        },
        "ca": {
            "labels": [item['_id'] for item in data_ca],
            "data": [item['ca_total'] for item in data_ca]
        }
    }


def get_nosql_data(periode='all'):
    """
    Récupère les stats avec un filtre temporel.
    """
    db = get_mongo_db()
    collection = db.ventes_menus

    # 1. Préparation du filtre de temps ($match)
    match_stage = {}
    if periode == '30j':
        date_limite = datetime.now() - timedelta(days=30)
        match_stage = {"$match": {"date_commande": {"$gte": date_limite}}}
    elif periode == '7j':
        date_limite = datetime.now() - timedelta(days=7)
        match_stage = {"$match": {"date_commande": {"$gte": date_limite}}}

    # 2. Construction dynamique des pipelines
    pipeline_quantite = []
    pipeline_ca = []

    # Si on a un filtre de date, on l'ajoute en TOUT PREMIER dans le pipeline
    if match_stage:
        pipeline_quantite.append(match_stage)
        pipeline_ca.append(match_stage)

    # On ajoute la suite (group et sort)
    pipeline_quantite.extend([
        {"$group": {"_id": "$titre_menu", "total_vendus": {"$sum": "$quantite"}}},
        {"$sort": {"total_vendus": -1}}
    ])

    pipeline_ca.extend([
        {"$group": {"_id": "$titre_menu", "ca_total": {"$sum": "$chiffre_affaires_brut"}}},
        {"$sort": {"ca_total": -1}}
    ])

    data_quantite = list(collection.aggregate(pipeline_quantite))
    data_ca = list(collection.aggregate(pipeline_ca))

    return {
        "quantite": {
            "labels": [item['_id'] for item in data_quantite],
            "data": [item['total_vendus'] for item in data_quantite]
        },
        "ca": {
            "labels": [item['_id'] for item in data_ca],
            "data": [item['ca_total'] for item in data_ca]
        }
    }