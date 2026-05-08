import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

load_dotenv()

# On importe les fonctions du dossier backend
from backend.user import create_user, login_user

# On configure Flask
app = Flask(
    __name__,
    # Pointe vers les fichiers HTML
    template_folder="frontend/templates",
    # Pointe vers les fichiers CSS/JS
    static_folder="frontend/static"
)

# Clé secrète obligatoire pour faire fonctionner la session et les messages flash()
app.secret_key = os.getenv("SECRET_KEY", "cle_secrete_de_secours_vite_et_gourmand")
@app.route('/')
def home():
    return "Bienvenue sur Vite & Gourmand !"

# Route pour déconnecter l'utilisateur
@app.route('/logout')
def logout():
    session.clear()  # Vide toutes les informations de connexion
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for('login_page'))

# Route pour gérer la connexion
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # Si l'utilisateur est déjà connecté, redirection vers l'accueil
    if 'user_prenom' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


        # Vérification de l'email, le mot de passe haché en BDD
        user = login_user(email, password)

        # 1. Si la connexion échoue (user est égal à False)
        if not user:
            # Préparation du message d'erreur en rouge
            flash("Adresse email ou mot de passe incorrect.", "error")
            # Chargement de la page login.html pour afficher l'erreur
            return render_template('auth/login.html')

        # 2. Si la connexion réussit
        # Enregistrement des données de l'utilisateur dans la session Flask
        session['user_id'] = user.get('id') or user.get('id_utilisateur')  # S'adapte au nom de ta clé primaire SQL
        session['user_prenom'] = user['prenom']
        session['user_nom'] = user['nom']
        session['user_role'] = user['role_id']

        flash(f"Connexion réussie ! Ravis de vous revoir {user['prenom']}.", "success")
        # Redirection vers la page d'accueil
        return redirect(url_for('home'))

    # Passage en méthode GET, affichage simple de la page
    return render_template('auth/login.html')

# Route pour afficher le formulaire d'inscription
@app.route('/register')
def register_page():
    return render_template('auth/register.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)