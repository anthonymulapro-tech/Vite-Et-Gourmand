import os
import bcrypt

# Détermination du chemin absolu vers le fichier SQL
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sql_file_path = os.path.join(base_dir, 'sql', '02_insert_data.sql')

# Sécurité si exécuté depuis la racine directement
if not os.path.exists(sql_file_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(base_dir, 'sql', '02_insert_data.sql')

print(f"Fichier SQL ciblé : {sql_file_path}")

try:
    with open(sql_file_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()

    # Liste des mots de passe en clair présents dans 02_insert_data.sql
    passwords_to_hash = [
        "ExempleMotDePasse1!",
        "ExempleMotDePasse2!",
        "ExempleMotDePasse3!"
        "ExempleMotDePasse4!",
        "ExempleMotDePasse5!",
        "ExempleMotDePasse6!"
        "ExempleMotDePasse7!",
        "ExempleMotDePasse8!",
        "ExempleMotDePasse9!"
    ]

    print("Hachage de tes mots de passe avec Bcrypt...")
    remplacements = 0
    for pwd in passwords_to_hash:
        # Remplacement uniquement si le mot de passe en clair est présent
        if f"'{pwd}'" in sql_content:
            salt = bcrypt.gensalt()
            hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), salt).decode('utf-8')
            sql_content = sql_content.replace(f"'{pwd}'", f"'{hashed_pwd}'")
            print(f"Securisation reussie pour : {pwd[:10]}...")
            remplacements += 1

    if remplacements > 0:
        with open(sql_file_path, 'w', encoding='utf-8') as file:
            file.write(sql_content)
        print(f"\nTermine ! Ton fichier 02_insert_data.sql a ete mis a jour avec de vrais hashes securises.")
    else:
        print("\nAucun mot de passe en clair trouve (ils ont peut-etre deja ete haches).")

except Exception as e:
    print(f"Erreur lors de la securisation : {e}")