from backend.database import get_connection
import bcrypt
import re
import mysql.connector

# Mot de passe utilisateur
def validate_password(password):
    # Critères : 10 caractères, 1 Maj, 1 min, 1 chiffre, 1 caractère spécial
    checks = [
        len(password) >= 10,
        re.search(r"[A-Z]", password),
        re.search(r"[a-z]", password),
        re.search(r"\d", password),
        re.search(r"[!@#$%^&*(),.?\":{}|<>_+\-]", password)
    ]
    return all(checks)

# Creation d'un compte utilisateur avec mot de passe haché.
def create_user(email, password, prenom, nom, telephone, pays, ville, adresse, code_postal):
    #Nettoyage des espaces.
    email = email.strip()
    password = password.strip()
    telephone = telephone.strip()
    code_postal = code_postal.strip()

    # Validation du mot de passe selon les critères
    if not validate_password(password):
        print("Le mot de passe ne respecte pas les critères de sécurité.")
        return False
        # Validation Téléphone (10 chiffres)
    if not (telephone.isdigit() and len(telephone) == 10):
        print("Le téléphone doit contenir exactement 10 chiffres.")
        return False

        # Validation Code Postal (5 chiffres)
    if not (code_postal.isdigit() and len(code_postal) == 5):
        print("Le code postal doit contenir exactement 5 chiffres.")
        return False

        # Validation Nom/Prénom (au moins 2 caractères)
    if len(nom) < 2 or len(prenom) < 2:
        print("Le nom et le prénom doivent avoir au moins 2 caractères.")
        return False

    # Hachage du mot de passe
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Insertion en base de données
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = """INSERT INTO utilisateur
                     ( email, password, prenom, nom, telephone, pays, ville, adresse, code_postal, role_id, est_actif)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 3, 1)"""
            # On stocke le mot de passe décodé pour le format VARCHAR de SQL
            valeurs = (
                email,
                hashed_password.decode('utf-8'),
                prenom,
                nom,
                telephone,
                pays,
                ville,
                adresse,
                code_postal
            )
            cursor.execute(sql, valeurs)
            conn.commit()
            print(f"Utilisateur {prenom} créé avec succès !")
            return True

        except mysql.connector.Error as err:
            # Gestion erreur email déjà utilisé (Code Erreur 1062 : Duplicate entry)
            if err.errno == 1062:
                print(f"L'adresse email '{email}' est déjà associée à un compte.")
            else:
                print(f"Erreur MySQL : {err}")
            return False

        except Exception as e:
            print(f"Erreur lors de l'insertion : {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False


def login_user(email, password):
    # Nettoyage
    email = email.strip()
    password = password.strip()

    conn = get_connection()
    if conn:
        try:
            # dictionary=True permet d'accéder aux colonnes par nom
            cursor = conn.cursor(dictionary=True)
            # Recherche de l'utilisateur par son email
            sql = "SELECT * FROM utilisateur WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user:
                # Vérification si le compte est actif
                if user['est_actif'] == 0:
                    print("Ce compte a été désactivé. Contactez l'administrateur.")
                    return False
                # Vérification du mot de passe
                password_byte = password.encode('utf-8')
                hashed_byte = user['password'].encode('utf-8')

                if bcrypt.checkpw(password_byte, hashed_byte):
                    print(f"Connexion réussie ! Bienvenue {user['prenom']}.")
                    return user
                else:
                    print("Mot de passe incorrect.")
            else:
                print("Aucun compte trouvé avec cet email.")

            return False

        except Exception as e:
            print(f"Erreur lors de la connexion : {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False


# Supprime un utilisateur de test pour réinitialiser l'état de la BDD.
def delete_test_user(email):

    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "DELETE FROM utilisateur WHERE email = %s"
            cursor.execute(sql, (email,))
            conn.commit()
            print(f"Nettoyage : L'utilisateur {email} a été supprimé pour le test.")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Supprimer ce mail pour valider les test
    delete_test_user("doublon.test@mail.com")

    # --- Tests pour create_user ---
    print("\n" + "=" * 45)
    print("Tests de vérification des données utilisateur")
    print("=" * 45)

    # TEST 1 : Mot de passe trop court (doit échouer)
    print("\n--- Test 1 : Mot de passe invalide (trop court) ---")
    create_user("test.mdp1@mail.com", "Court1!", "Jean", "Test", "0601020304", "France", "Bordeaux", "Rue A", "33000")

    # TEST 2 : Mot de passe sans caractère spécial (doit échouer)
    print("\n--- Test 2 : Mot de passe invalide (pas de spécial) ---")
    create_user("test.mdp2@mail.com", "MDP100spécial", "Marc", "Test", "0602030405", "France", "Paris", "Rue B", "33000")

    # TEST 3 : Inscription valide
    print("\n--- Test 3 : Inscription valide ---")
    create_user("doublon.test@mail.com", "ViteGourmand2026!", "Abdel", "Test", "0603040506", "France", "Lyon", "Rue C", "33000")

    # TEST 4 : Test du doublon (doit échouer car l'email du Test 3 existe déjà)
    print("\n--- Test 4 : Tentative de doublon email ---")
    create_user("doublon.test@mail.com", "AutreMdp123!", "Doublon", "Email", "0604050607", "France", "Marseille", "Rue D", "33000")

    # Test 5 : Téléphone incorrect (doit échouer)
    print("\n--- Test 5 : Téléphone invalide (lettres) ---")
    create_user("tel.err@mail.com", "MdpSecurise123!", "Jean", "Erreur", "06AB030405", "France", "Paris", "Rue X",
                "75000")

    # Test 6 : Code Postal incorrect (doit échouer)
    print("\n--- Test 6 : Code Postal invalide (trop long) ---")
    create_user("cp.err@mail.com", "MdpSecurise123!", "Marc", "Erreur", "0601020304", "France", "Paris", "Rue Y",
                "750001")


    # --- Tests pour login_user ---
    print("\n" + "=" * 26)
    print("Tests de connexion (Login)")
    print("=" * 26)

    # TEST 1 : Connexion réussie (Identifiants exacts)
    # On teste avec l'utilisateur créé au Test 3
    print("\n--- Test 1 : Connexion réussie ---")
    login_user("doublon.test@mail.com", "ViteGourmand2026!")

    # TEST 2 : Mot de passe erroné
    print("\n--- Test 2 : Mot de passe incorrect ---")
    login_user("doublon.test@mail.com", "MauvaisMdp123!")

    # TEST 3 : Email inexistant
    print("\n--- Test 3 : Email inconnu ---")
    login_user("inconnu@mail.com", "NimporteQuoi123!")

    # TEST 4 : Test de la robustesse (Espaces inutiles)
    # Le .strip() doit permettre la connexion malgré les espaces
    print("\n--- Test 4 : Robustesse (Espaces en trop) ---")
    login_user("  doublon.test@mail.com  ", "ViteGourmand2026!  ")