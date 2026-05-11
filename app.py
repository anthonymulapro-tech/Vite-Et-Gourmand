import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

load_dotenv()

# ==========================================================================
# IMPORTS DU BACKEND (On sépare la logique SQL)
# ==========================================================================
from backend.user import create_user, login_user, validate_password, email_exists
# Importation des futures fonctions SQL
from backend.menu import get_all_menus
from backend.review import get_validated_reviews
from backend.contact import save_contact_message
from backend.schedule import get_schedule

# Configuration de Flask
app = Flask(
    __name__,
    template_folder="frontend/templates",  # Pointe vers les fichiers HTML
    static_folder="frontend/static"  # Pointe vers les fichiers CSS/JS
)

# Sécurisation des cookies et clé secrète
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.secret_key = os.getenv("SECRET_KEY")



# Injecteurs de données globales, exemple les horaires sur toute les pages
@app.context_processor
def inject_global_data():
    try:
        schedule = get_schedule()
    except Exception as e:
        print(f"Erreur lors de la récupération des horaires : {e}")
        schedule = []
    return dict(horaires_ouverture=schedule)


# Route d'accueil (Affiche les avis dynamiques)
@app.route('/')
def home():
    try:
        # Récupère uniquement les avis validés par l'administration
        les_avis = get_validated_reviews()
    except Exception as e:
        print(f"Erreur de chargement des avis : {e}")
        les_avis = []

    return render_template('home.html', les_avis=les_avis)


# Route de contact (Soumission de formulaire)
@app.route('/contact', methods=['POST'])
def contact():
    # Récupération directe via les attributs "name" harmonisés avec le SQL
    motif = request.form.get('motif')
    prenom = request.form.get('prenom_contact')
    nom = request.form.get('nom_contact')
    email = request.form.get('email_contact')
    description = request.form.get('description_contact')

    # Double validation de sécurité côté serveur (Python)
    if not motif or not prenom or not nom or not email or not description:
        flash("Veuillez remplir tous les champs du formulaire.", "error")
        return redirect(url_for('home'))

    # Tentative d'enregistrement dans la table message_contact
    try:
        success = save_contact_message(
            nom_contact=nom,
            prenom_contact=prenom,
            motif=motif,
            description_contact=description,
            email_contact=email
        )
        if success:
            flash("Votre message a bien été envoyé ! Nous vous répondrons très rapidement.", "success")
        else:
            flash("Une erreur technique est survenue lors de l'envoi.", "error")
    except Exception as e:
        print(f"Erreur d'insertion du message de contact : {e}")
        flash("Impossible d'envoyer le message. Service indisponible.", "error")

    return redirect(url_for('home'))


# Route d'affichage des menus (Dynamique SQL)
@app.route('/menus')
def menus_page():
    try:
        # Récupère tous les menus avec leurs prix, stocks, régimes, thèmes, etc.
        catalogue_menus = get_all_menus()
    except Exception as e:
        print(f"Erreur de chargement du catalogue : {e}")
        catalogue_menus = None

    return render_template('menus.html', menus=catalogue_menus)


# Route pour gérer la connexion
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'user_prenom' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérification email existant
        if not email_exists(email):
            return render_template('auth/login.html', email_error=True, email_saved=email)

        # L'email est valide, mais vérification du mot de passe
        user = login_user(email, password)

        if not user:
            return render_template('auth/login.html', password_error=True, email_saved=email)

        # Connexion réussie !
        session['user_id'] = user.get('id') or user.get('id_utilisateur')
        session['user_prenom'] = user['prenom']
        session['user_nom'] = user['nom']
        session['user_role'] = user['role_id']

        flash(f"Connexion réussie ! Ravis de vous revoir {user['prenom']}.", "success")
        return redirect(url_for('home'))

    return render_template('auth/login.html')


# Route pour gérer l'inscription d'un nouvel utilisateur
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if 'user_prenom' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        prenom = request.form.get('prenom')
        nom = request.form.get('nom')
        telephone = request.form.get('telephone')
        adresse = request.form.get('adresse')
        ville = request.form.get('ville')
        code_postal = request.form.get('code_postal')
        pays = request.form.get('pays', 'France')

        # Double vérification de sécurité en Python
        if not email or not password or not prenom or not nom:
            flash("Veuillez remplir tous les champs obligatoires.", "error")
            return render_template('auth/register.html')

        # Validation du mot de passe
        if not validate_password(password):
            return render_template('auth/register.html', password_error=True)

        # Validation du format Téléphone (10 chiffres)
        if telephone and not (telephone.strip().isdigit() and len(telephone.strip()) == 10):
            flash("Le numéro de téléphone doit contenir exactement 10 chiffres.", "error")
            return render_template('auth/register.html')

        # Validation du format Code Postal (5 chiffres)
        if code_postal and not (code_postal.strip().isdigit() and len(code_postal.strip()) == 5):
            flash("Le code postal doit contenir exactement 5 chiffres.", "error")
            return render_template('auth/register.html')

        # Vérification de l'email doublon
        if email_exists(email):
            return render_template('auth/register.html', email_error=True)

        # Tentative de création
        success = create_user(
            email=email,
            password=password,
            prenom=prenom,
            nom=nom,
            telephone=telephone,
            pays=pays,
            ville=ville,
            adresse=adresse,
            code_postal=code_postal
        )

        if success:
            flash("Votre compte a été créé avec succès\u00a0! Connectez-vous.", "success")
            return redirect(url_for('login_page'))
        else:
            flash("Une erreur technique est survenue. Veuillez réessayer plus tard.", "error")
            return render_template('auth/register.html')

    return render_template('auth/register.html')


# Route pour déconnecter l'utilisateur
@app.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for('login_page'))

# Route temporaire pour la fiche détaillée (évite le plantage de url_for dans menus.html)
@app.route('/menu/<int:menu_id>')
def menu_detail(menu_id):
    return f"<h1>Détail du menu {menu_id}</h1><p>Cette page est actuellement en cours de développement sur ta prochaine branche !</p><a href='{url_for('menus_page')}'>Retour aux menus</a>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)