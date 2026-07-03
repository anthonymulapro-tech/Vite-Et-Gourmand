import os
import bcrypt

# CLASSE UTILITAIRE (Boîte à outils de Sécurité)
class SecurityUtils:
    # Constante de classe : La liste par défaut des mots de passe à sécuriser
    DEFAULT_PASSWORDS = [
        "ExempleMotDePasse1!",
        "ExempleMotDePasse2!",
        "ExempleMotDePasse3!",
        "ExempleMotDePasse4!",
        "ExempleMotDePasse5!",
        "ExempleMotDePasse6!",
        "ExempleMotDePasse7!",
        "ExempleMotDePasse8!",
        "ExempleMotDePasse9!"
    ]

    @staticmethod
    def get_sql_file_path():
        """Détermine le chemin absolu vers le fichier SQL de manière dynamique."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_file_path = os.path.join(base_dir, 'sql', '02_insert_data.sql')

        # Sécurité si exécuté depuis le dossier backend directement
        if not os.path.exists(sql_file_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            sql_file_path = os.path.join(base_dir, 'sql', '02_insert_data.sql')

        return sql_file_path

    @classmethod
    def secure_sql_file(cls, passwords=None):
        """
        Parcourt le fichier SQL et remplace les mots de passe en clair par des hashs bcrypt.
        Utilise @classmethod pour accéder à cls.DEFAULT_PASSWORDS et cls.get_sql_file_path()
        """
        sql_file_path = cls.get_sql_file_path()
        print(f"Fichier SQL ciblé : {sql_file_path}")

        # Si on ne fournit pas de liste, on utilise celle de la classe
        passwords_to_hash = passwords if passwords else cls.DEFAULT_PASSWORDS

        try:
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()

            print("Hachage de tes mots de passe avec Bcrypt...")
            remplacements = 0

            for pwd in passwords_to_hash:
                # Remplacement uniquement si le mot de passe en clair est présent
                if f"'{pwd}'" in sql_content:
                    salt = bcrypt.gensalt()
                    hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), salt).decode('utf-8')
                    sql_content = sql_content.replace(f"'{pwd}'", f"'{hashed_pwd}'")
                    print(f"Sécurisation réussie pour : {pwd[:10]}...")
                    remplacements += 1

            if remplacements > 0:
                with open(sql_file_path, 'w', encoding='utf-8') as file:
                    file.write(sql_content)
                print(f"\nTerminé ! Ton fichier 02_insert_data.sql a été mis à jour avec de vrais hashes sécurisés.")
            else:
                print("\nAucun mot de passe en clair trouvé (ils ont peut-être déjà été hachés).")

        except Exception as e:
            print(f"Erreur lors de la sécurisation : {e}")


# ==========================================
# ZONE D'EXÉCUTION DIRECTE (Script)
# ==========================================
if __name__ == "__main__":
    print("--- DÉMARRAGE DU SCRIPT DE SÉCURITÉ ---")
    SecurityUtils.secure_sql_file()