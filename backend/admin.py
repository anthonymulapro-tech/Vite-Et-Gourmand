import bcrypt

# REPOSITORY (Le Mécanicien de l'Administration)
class AdminRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_employees(self):
        """Récupère la liste de tous les employés (role_id = 2)."""
        try:
            # "with" gère la fermeture automatique du curseur
            with self.db.cursor(dictionary=True) as cursor:
                sql = """
                      SELECT utilisateur_id, prenom, nom, email, est_actif
                      FROM utilisateur
                      WHERE role_id = 2
                      ORDER BY nom ASC, prenom ASC
                      """
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération des employés : {e}")
            return []

    def create_employee_account(self, prenom, nom, email, plain_password):
        """Crée un compte employé avec un mot de passe haché et un rôle forcé à 2."""
        try:
            with self.db.cursor() as cursor:
                # 1. Vérification si l'email existe déjà
                cursor.execute("SELECT COUNT(*) FROM utilisateur WHERE email = %s", (email,))
                if cursor.fetchone()[0] > 0:
                    return False, "Cet email est déjà utilisé par un autre compte."

                # 2. Hachage sécurisé du mot de passe
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(plain_password.strip().encode('utf-8'), salt).decode('utf-8')

                # 3. Insertion en forçant le role_id à 2 (Employé) et est_actif à 1
                sql = """
                      INSERT INTO utilisateur (prenom, nom, email, password, role_id, est_actif)
                      VALUES (%s, %s, %s, %s, 2, 1)
                      """
                cursor.execute(sql, (prenom, nom, email, hashed_password))
                self.db.commit()

                return True, "Le compte employé a été créé avec succès."

        except Exception as e:
            print(f"Erreur SQL lors de la création de l'employé : {e}")
            return False, "Une erreur technique est survenue lors de la création."

    def toggle_employee_status(self, employe_id, est_actif_val):
        """Active ou désactive un compte employé."""
        try:
            with self.db.cursor() as cursor:
                # Ajout de "AND role_id = 2" pour sécuriser et empêcher de désactiver un Admin par erreur
                sql = "UPDATE utilisateur SET est_actif = %s WHERE utilisateur_id = %s AND role_id = 2"
                cursor.execute(sql, (est_actif_val, employe_id))
                self.db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur SQL lors de la modification du statut de l'employé #{employe_id} : {e}")
            return False