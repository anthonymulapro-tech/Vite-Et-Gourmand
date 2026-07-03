import re
import bcrypt
import mysql.connector


# ==========================================
# 1. LE MODÈLE (L'Entité Utilisateur)
# Gère la donnée pure, les validations et la sécurité.
# ==========================================
class User:
    def __init__(self, email, password, prenom, nom, telephone, pays, ville, adresse, code_postal, role_id=3,
                 est_actif=1, utilisateur_id=None):
        self.utilisateur_id = utilisateur_id
        self.email = email.strip() if email else ""
        self.password = password.strip() if password else ""
        self.prenom = prenom.strip() if prenom else ""
        self.nom = nom.strip() if nom else ""
        self.telephone = telephone.strip() if telephone else ""
        self.pays = pays
        self.ville = ville
        self.adresse = adresse
        self.code_postal = code_postal.strip() if code_postal else ""
        self.role_id = role_id
        self.est_actif = est_actif

    def is_valid_for_creation(self):
        """Vérifie si les données saisies par l'utilisateur sont conformes avant l'inscription."""
        if not self.validate_password(self.password):
            print("Erreur : Le mot de passe ne respecte pas les critères de sécurité.")
            return False
        if not (self.telephone.isdigit() and len(self.telephone) == 10):
            print("Erreur : Le téléphone doit contenir exactement 10 chiffres.")
            return False
        if not (self.code_postal.isdigit() and len(self.code_postal) == 5):
            print("Erreur : Le code postal doit contenir exactement 5 chiffres.")
            return False
        if len(self.nom) < 2 or len(self.prenom) < 2:
            print("Erreur : Le nom et le prénom doivent avoir au moins 2 caractères.")
            return False
        return True

    @staticmethod
    def validate_password(password):
        if not password:
            return False
        checks = [
            len(password) >= 10,
            re.search(r"[A-Z]", password),
            re.search(r"[a-z]", password),
            re.search(r"\d", password),
            re.search(r"[!@#$%^&*(),.?\":{}|<>_+\-]", password)
        ]
        return all(checks)

    def hash_password(self):
        """Hache le mot de passe et remplace l'attribut actuel."""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(self.password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, plain_password):
        """Vérifie si le mot de passe en clair correspond au hash enregistré."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

    def to_dict(self):
        """
        Astuce de transition : Transforme l'objet en dictionnaire.
        Cela permet à app.py de continuer à faire user['prenom'] sans planter.
        """
        return {
            'utilisateur_id': self.utilisateur_id,
            'email': self.email,
            'password': self.password,
            'prenom': self.prenom,
            'nom': self.nom,
            'telephone': self.telephone,
            'pays': self.pays,
            'ville': self.ville,
            'adresse': self.adresse,
            'code_postal': self.code_postal,
            'role_id': self.role_id,
            'est_actif': self.est_actif
        }


# ==========================================
# 2. LE REPOSITORY (Le Mécanicien)
# S'occupe exclusivement de parler avec MySQL.
# ==========================================
class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def email_exists(self, email):
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT utilisateur_id FROM utilisateur WHERE email = %s", (email.strip(),))
            return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            print(f"Erreur SQL email_exists : {err}")
            return False
        finally:
            cursor.close()

    def create_user(self, user_obj):
        """Prend l'objet User complet en paramètre et l'insère en base."""
        if not user_obj.is_valid_for_creation():
            return False

        # Hachage du mot de passe de l'objet juste avant de l'envoyer à la BDD
        user_obj.hash_password()

        cursor = self.db.cursor()
        try:
            sql = """INSERT INTO utilisateur
                     (email, password, prenom, nom, telephone, pays, ville, adresse, code_postal, role_id, est_actif)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            valeurs = (
                user_obj.email, user_obj.password, user_obj.prenom, user_obj.nom,
                user_obj.telephone, user_obj.pays, user_obj.ville, user_obj.adresse,
                user_obj.code_postal, user_obj.role_id, user_obj.est_actif
            )
            cursor.execute(sql, valeurs)
            self.db.commit()
            print(f"Utilisateur {user_obj.prenom} créé avec succès !")
            return True

        except mysql.connector.Error as err:
            if err.errno == 1062:
                print(f"L'adresse email '{user_obj.email}' est déjà associée à un compte.")
            else:
                print(f"Erreur MySQL : {err}")
            return False
        except Exception as e:
            print(f"Erreur lors de l'insertion : {e}")
            return False
        finally:
            cursor.close()

    def login_user(self, email, password):
        email = email.strip()
        password = password.strip()

        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM utilisateur WHERE email = %s", (email,))
            user_data = cursor.fetchone()

            if user_data:
                if user_data['est_actif'] == 0:
                    print("Ce compte a été désactivé.")
                    return False

                # Recréation d'un objet User complet grâce aux données de la base
                user = User(**user_data)

                # Utilisation de la méthode de l'objet pour vérifier le mot de passe
                if user.check_password(password):
                    print(f"Connexion réussie ! Bienvenue {user.prenom}.")
                    return user.to_dict()
                else:
                    print("Mot de passe incorrect.")
            else:
                print("Aucun compte trouvé.")
            return False

        except Exception as e:
            print(f"Erreur lors de la connexion : {e}")
            return False
        finally:
            cursor.close()

    def get_user_by_id(self, user_id):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM utilisateur WHERE utilisateur_id = %s", (user_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erreur get_user_by_id : {e}")
            return None
        finally:
            cursor.close()

    def update_user_profile(self, user_id, prenom, nom, telephone, adresse, ville, code_postal, pays):
        cursor = self.db.cursor()
        try:
            query = """UPDATE utilisateur
                       SET prenom=%s, \
                           nom=%s, \
                           telephone=%s, \
                           adresse=%s, \
                           ville=%s, \
                           code_postal=%s, \
                           pays=%s
                       WHERE utilisateur_id = %s"""
            cursor.execute(query, (prenom, nom, telephone, adresse, ville, code_postal, pays, user_id))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Erreur mise à jour profil : {e}")
            return False
        finally:
            cursor.close()

    def delete_test_user(self, email):
        cursor = self.db.cursor()
        try:
            sql = "DELETE FROM utilisateur WHERE email = %s"
            cursor.execute(sql, (email,))
            self.db.commit()
            print(f"Nettoyage : Utilisateur {email} supprimé.")
        finally:
            cursor.close()