import os
from pymongo import MongoClient
from datetime import datetime, timedelta

class AdminDataRepository:
    def __init__(self, mysql_connection=None):
        """
        Le paramètre mysql_connection est optionnel.
        On en a besoin uniquement pour la synchronisation, pas pour la lecture des graphiques.
        """
        self.mysql_db = mysql_connection

    def _get_mongo_db(self):
        """Méthode privée qui établit la connexion avec le cluster MongoDB local."""
        mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/vite_et_gourmand_stats")
        client = MongoClient(mongo_uri)
        return client.get_database()

    def sync_mysql_to_mongo(self):
        """Processus ETL : Extrait de MySQL, nettoie, et insère dans NoSQL."""
        if not self.mysql_db:
            return False, "Erreur de connexion MySQL non fournie au Repository."

        db = self._get_mongo_db()
        collection = db.ventes_menus

        try:
            with self.mysql_db.cursor(dictionary=True) as cursor:
                sql = """
                      SELECT c.reference_commande,
                             c.date_commande,
                             m.titre_menu,
                             cm.quantite,
                             (cm.quantite * m.prix_par_personne) AS chiffre_affaires_brut
                      FROM commande_menu cm
                               JOIN commande c ON cm.commande_id = c.commande_id
                               JOIN menu m ON cm.menu_id = m.menu_id
                      WHERE c.statut_commande != 'Annulé'
                      """
                cursor.execute(sql)
                lignes_ventes = cursor.fetchall()

            if lignes_ventes:
                for ligne in lignes_ventes:
                    if ligne['chiffre_affaires_brut']:
                        ligne['chiffre_affaires_brut'] = float(ligne['chiffre_affaires_brut'])

                collection.delete_many({})
                collection.insert_many(lignes_ventes)

            return True, f"Synchronisation réussie : {len(lignes_ventes)} lignes de ventes importées."

        except Exception as e:
            print(f"Erreur lors de la synchro ETL : {e}")
            return False, "Erreur technique lors de la migration vers MongoDB."

    def get_nosql_data(self, periode='all'):
        """Récupère les stats depuis MongoDB avec un filtre temporel."""
        db = self._get_mongo_db()
        collection = db.ventes_menus

        match_stage = {}
        if periode == '30j':
            date_limite = datetime.now() - timedelta(days=30)
            match_stage = {"$match": {"date_commande": {"$gte": date_limite}}}
        elif periode == '7j':
            date_limite = datetime.now() - timedelta(days=7)
            match_stage = {"$match": {"date_commande": {"$gte": date_limite}}}

        pipeline_quantite = []
        pipeline_ca = []

        if match_stage:
            pipeline_quantite.append(match_stage)
            pipeline_ca.append(match_stage)

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