import os
import stripe

from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

from backend.user import create_user, login_user, validate_password, email_exists
from backend.cart import calculer_prix_total
from backend.order import create_order
# ==========================================================================
# IMPORTS DU BACKEND (On sépare la logique SQL)
# ==========================================================================
from backend.menu import get_all_menus
from backend.review import get_validated_reviews
from backend.contact import save_contact_message
from backend.schedule import get_schedule
from backend.menu_model import get_menu_details
from backend.database import get_connection
from backend.order_history import get_user_orders

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
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

    # On récupère l'éventuelle page suivante
    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email_exists(email):
            return render_template('auth/login.html', email_error=True, email_saved=email)

        user = login_user(email, password)
        if not user:
            return render_template('auth/login.html', password_error=True, email_saved=email)

        # Connexion réussie
        session['user_id'] = user.get('utilisateur_id')
        session['user_prenom'] = user['prenom']
        session['user_nom'] = user['nom']
        session['user_role'] = user['role_id']

        # Redirection intelligente : vers next_page si elle existe, sinon vers home
        return redirect(next_page or url_for('home'))

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

@app.route('/menu/<int:id_menu>')
def detail_menu(id_menu):
    db = get_connection()  # Ouverture de la connexion
    if db is None:
        return "Erreur de connexion à la base de données", 500

    try:
        # On passe la connexion et l'ID au modèle
        menu = get_menu_details(db, id_menu)

        if menu is None:
            return "Menu non trouvé", 404

        return render_template('detail_menu.html', menu=menu)
    finally:
        # Fermeture
        db.close()


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    id_menu_form = request.form.get('id_menu')
    raw_quantity = request.form.get('quantity')

    try:
        quantite = int(raw_quantity)
    except (ValueError, TypeError):
        return redirect(url_for('menus_page'))

    db = get_connection()
    menu = get_menu_details(db, id_menu_form)
    db.close()

    if not menu:
        return redirect(url_for('menus_page'))

    # Récupération des 3 prix calculés
    prix_calcules = calculer_prix_total(
        quantite=quantite,
        prix_unitaire=float(menu['prix_par_personne']),
        min_convives=menu['nombre_personne_min'],
        seuil_reduction=menu['seuil_reduction'],
        pourcentage_reduction=menu['pourcentage_reduction']
    )

    if 'panier' not in session:
        session['panier'] = []

    # Enregistrement du tout en session
    session['panier'].append({
        'id_menu': menu['menu_id'],
        'name': menu['titre_menu'],
        'quantity': quantite,
        'price': float(menu['prix_par_personne']),
        'prix_brut': prix_calcules['prix_brut'],
        'remise': prix_calcules['remise'],
        'total_price': prix_calcules['prix_final']
    })

    session.modified = True
    return redirect(url_for('cart'))


@app.route('/cart', methods=['GET'])
def cart():
    cart_items = session.get('panier', [])

    # Calcule le vrai Sous-total HT (SANS les remises)
    subtotal = sum(item.get('prix_brut', item['total_price']) for item in cart_items)

    # Calcule le total des remises cumulées
    total_discount = sum(item.get('remise', 0) for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, total_discount=total_discount)


@app.route('/clear-cart')
def clear_cart():
    # On vide la clé 'panier' de la session
    session.pop('panier', None)
    session.modified = True

    # Redirection sur le panier ( message de panier vide + voir les menus )
    return redirect(url_for('cart'))


# Route pour gérer la validation du panier ( à faire ensuite )
@app.route('/checkout', methods=['POST'])
def checkout_step_1():
    """Étape 1 : Enregistrement des options choisies dans le panier et on redirige vers le formulaire d'adresse."""
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour continuer.", "error")
        return redirect(url_for('login_page', next=url_for('cart')))

    # On stocke les options temporaires en session pour les retrouver à l'étape finale
    session['checkout_options'] = {
        'delivery_zone': request.form.get('delivery_zone'),
        'distance_km': float(request.form.get('distance_km', 0) or 0),
        'need_material': request.form.get('need_material')
    }
    session.modified = True
    return redirect(url_for('order_details'))


@app.route('/order-details', methods=['GET'])
def order_details():
    """Étape 2 : Affiche le formulaire d'adresse précise."""
    if 'user_id' not in session or 'checkout_options' not in session:
        return redirect(url_for('cart'))

    cart_items = session.get('panier', [])
    total_menus = sum(item['total_price'] for item in cart_items)

    # Récupération des frais de livraison calculés
    opts = session['checkout_options']
    total_delivery = 5 + (opts['distance_km'] * 0.59) if opts['delivery_zone'] == 'outside' else 0

    # Date minimale de livraison (J+2)
    min_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

    return render_template('validate_order.html',
                           total_menus=total_menus,
                           total_delivery=total_delivery,
                           min_date=min_date)


@app.route('/confirm-order', methods=['POST'])
def confirm_order():
    """Génère la session de paiement Stripe."""
    if 'user_id' not in session: return redirect(url_for('login_page'))

    # Sauvegarde des données de livraison finales en session avant de partir sur Stripe
    opts = session.get('checkout_options', {})
    opts['adresse'] = request.form.get('adresse')
    opts['ville'] = request.form.get('ville')
    opts['cp'] = request.form.get('code_postal')
    opts['date_prestation'] = request.form.get('date_prestation')
    opts['heure_livraison'] = request.form.get('heure_livraison')
    session['checkout_options'] = opts
    session.modified = True

    cart_items = session.get('panier', [])
    total_menus = sum(item['total_price'] for item in cart_items)
    total_delivery = 5 + (opts['distance_km'] * 0.59) if opts['delivery_zone'] == 'outside' else 0

    # Création des "Lignes" pour Stripe
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': item['name']},
                'unit_amount': int((item['total_price'] / item['quantity']) * 100),
            },
            'quantity': item['quantity'],
        })

    # Ajout des frais de livraison comme un produit à part
    if total_delivery > 0:
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': 'Frais de livraison'},
                'unit_amount': int(total_delivery * 100),
            },
            'quantity': 1,
        })

    try:
        # Création de la session Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', _external=True),
            cancel_url=url_for('payment_cancel', _external=True),
        )
        # Redirection vers la page de paiement sécurisée de Stripe
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        flash(f"Erreur avec le service de paiement : {e}", "error")
        return redirect(url_for('order_details'))


@app.route('/payment-success')
def payment_success():
    """Le client a payé, on insère la commande en base de données."""
    if 'user_id' not in session or 'checkout_options' not in session:
        return redirect(url_for('home'))

    opts = session['checkout_options']
    cart_items = session.get('panier', [])

    total_menus = sum(item['total_price'] for item in cart_items)
    total_delivery = 5 + (opts['distance_km'] * 0.59) if opts['delivery_zone'] == 'outside' else 0

    success, result = create_order(
        utilisateur_id=session['user_id'],
        cart_items=cart_items,
        prix_menu=total_menus,
        prix_livraison=total_delivery,
        pret_materiel=opts['need_material'],
        adresse_livraison=opts['adresse'],
        ville_livraison=opts['ville'],
        code_postal_livraison=opts['cp'],
        date_prestation=opts['date_prestation'],
        heure_livraison=opts['heure_livraison']
    )

    if success:
        session.pop('panier', None)
        session.pop('checkout_options', None)
        # Utilisation de la succès
        return render_template('success.html', reference=result)
    else:
        flash(result, "error")
        return redirect(url_for('cart'))


@app.route('/payment-cancel')
def payment_cancel():
    """L'utilisateur a annulé le paiement sur la page Stripe."""
    return redirect(url_for('order_details'))
# Route pour déconnecter l'utilisateur

@app.route('/my-orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    # 1. On va chercher les commandes du client
    commandes = get_user_orders(session['user_id'])

    # 2. On les envoie à la page HTML !
    return render_template('my_orders.html', commandes=commandes)
@app.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)