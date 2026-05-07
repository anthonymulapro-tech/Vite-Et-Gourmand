from database import get_connection
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


    # 1. Validation du mot de passe selon les critères
    if not validate_password(password):
        print("Le mot de passe ne respecte pas les critères de sécurité.")
        return False

    # 2. Hachage du mot de passe
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # 3. Insertion en base de données
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

if __name__ == "__main__":
    print("Démarrage des tests unitaires pour user.py...")

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