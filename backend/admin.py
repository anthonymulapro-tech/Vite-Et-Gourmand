import bcrypt
from .database import get_connection


def get_all_employees():
    """Récupère la liste de tous les employés (role_id = 2)."""
    connection = get_connection()
    if not connection:
        return []
    try:
        with connection.cursor(dictionary=True) as cursor:
            # On ne récupère que les employés, jamais l'admin (1) ni les clients (3)
            sql = """
                  SELECT utilisateur_id, prenom, nom, email, est_actif
                  FROM utilisateur
                  WHERE role_id = 2
                  ORDER BY nom ASC, prenom ASC \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Erreur lors de la récupération des employés : {e}")
        return []
    finally:
        connection.close()


def create_employee_account(prenom, nom, email, plain_password):
    """Crée un compte employé avec un mot de passe haché et un rôle forcé à 2."""
    connection = get_connection()
    if not connection:
        return False, "Erreur de connexion à la base de données."

    try:
        with connection.cursor() as cursor:
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
                  VALUES (%s, %s, %s, %s, 2, 1) \
                  """
            cursor.execute(sql, (prenom, nom, email, hashed_password))
            connection.commit()

            return True, "Le compte employé a été créé avec succès."

    except Exception as e:
        print(f"Erreur SQL lors de la création de l'employé : {e}")
        return False, "Une erreur technique est survenue lors de la création."
    finally:
        connection.close()


def toggle_employee_status(employe_id, est_actif_val):
    """Active ou désactive un compte employé."""
    connection = get_connection()
    if not connection:
        return False
    try:
        with connection.cursor() as cursor:
            # On ajoute "AND role_id = 2" pour sécuriser et empêcher de désactiver un Admin par erreur
            sql = "UPDATE utilisateur SET est_actif = %s WHERE utilisateur_id = %s AND role_id = 2"
            cursor.execute(sql, (est_actif_val, employe_id))
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur SQL lors de la modification du statut de l'employé #{employe_id} : {e}")
        return False
    finally:
        connection.close()