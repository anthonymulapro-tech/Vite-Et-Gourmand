import os
import stripe

from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from dotenv import load_dotenv

from backend.user import create_user, login_user, validate_password, email_exists, get_user_by_id, update_user_profile
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
from backend.order_history import get_user_orders, get_order_details, cancel_client_order, add_client_review

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

# Configuration de Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 2525))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_DEFAULT_SENDER'] = ('Vite & Gourmand', 'noreply@viteetgourmand.fr')

mail = Mail(app)

def send_html_email(subject, recipient, template_name, **kwargs):
    """Fonction globale pour envoyer des e-mails au format HTML."""
    try:
        msg = Message(subject, recipients=[recipient])
        msg.html = render_template(template_name, **kwargs)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail [{subject}] : {e}")
        return False


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
             # E-mail de notification
            send_html_email(
                subject=f"🧠 [Contact] {motif} - {prenom} {nom}",
                recipient="admin@viteetgourmand.fr",
                template_name="emails/email_contact.html",
                motif=motif,
                prenom=prenom,
                nom=nom,
                email=email,
                description=description
            )
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

        confirm_password = request.form.get('confirm_password')

        # 1. Vérification de la correspondance des mots de passe
        if password != confirm_password:
            # On renvoie la page avec la variable d'erreur à True
            return render_template('auth/register.html', confirm_password_error=True)

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
            # Envoi de l'e-mail de bienvenue
            send_html_email(
                subject="Bienvenue chez Vite & Gourmand !",
                recipient=email,
                template_name="emails/welcome.html",
                prenom=prenom
            )

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

    # 1. Récupération des infos de l'utilisateur en BDD
    user_id = session['user_id']
    current_user = get_user_by_id(user_id)

    cart_items = session.get('panier', [])
    total_menus = sum(item['total_price'] for item in cart_items)

    # Récupération des frais de livraison calculés
    opts = session['checkout_options']
    total_delivery = 5 + (opts['distance_km'] * 0.59) if opts['delivery_zone'] == 'outside' else 0

    # Date minimale de livraison (J+2)
    min_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

    # 2.  'user=current_user' AU TEMPLATE HTML
    return render_template('validate_order.html',
                           total_menus=total_menus,
                           total_delivery=total_delivery,
                           min_date=min_date,
                           user=current_user)


@app.route('/confirm-order', methods=['POST'])
def confirm_order():
    if 'user_id' not in session: return redirect(url_for('login_page'))

    # Sauvegarde des données de livraison avec LES BONS NOMS
    opts = session.get('checkout_options', {})
    opts['adresse_livraison'] = request.form.get('adresse_livraison')
    opts['ville_livraison'] = request.form.get('ville_livraison')
    opts['code_postal_livraison'] = request.form.get('code_postal_livraison')
    opts['date_prestation'] = request.form.get('date_prestation')
    opts['heure_livraison'] = request.form.get('heure_livraison')
    session['checkout_options'] = opts
    session.modified = True

    cart_items = session.get('panier', [])
    total_delivery = 5 + (opts.get('distance_km', 0) * 0.59) if opts.get('delivery_zone') == 'outside' else 0

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
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment_cancel', _external=True),
            # METADATA AVEC LES NOMS ALIGNÉS !
            metadata={
                'adresse_livraison': str(opts.get('adresse_livraison', '')),
                'ville_livraison': str(opts.get('ville_livraison', '')),
                'code_postal_livraison': str(opts.get('code_postal_livraison', '')),
                'date_prestation': str(opts.get('date_prestation', '')),
                'heure_livraison': str(opts.get('heure_livraison', '')),
                'pret_materiel': str(opts.get('need_material', False)),
                'distance_km': str(opts.get('distance_km', 0)),
                'delivery_zone': str(opts.get('delivery_zone', 'inside'))
            }
        )
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        flash(f"Erreur avec le service de paiement : {e}", "error")
        return redirect(url_for('order_details'))


@app.route('/payment-success')
def payment_success():
    # 1. Récupération de l'ID envoyé par Stripe
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home'))

    # 2. Demande d'infos de session à Stripe
    stripe_session = stripe.checkout.Session.retrieve(session_id)
    metadata = stripe_session.metadata

    # --- Fonction pour lire le metadata Stripe ---
    def get_meta(key, default_value=''):
        if not metadata:
            return default_value
        try:
            # Lecture de la clé comme dans un dictionnaire standard
            return metadata[key]
        except Exception:
            return default_value

    # -----------------------------------------------------

    # 3. Récupération du  panier
    cart_items = session.get('panier', [])
    if not cart_items:
        return redirect(url_for('home'))

    # 4. Calculs des totaux
    total_menus = sum(item['total_price'] for item in cart_items)

    # Récupération de la valeur brute avec la fonction sécurisée
    raw_dist = get_meta('distance_km', '0')

    # Converssion en float
    try:
        dist_km = float(raw_dist) if raw_dist else 0.0
    except (ValueError, TypeError):
        dist_km = 0.0

    total_delivery = 5 + (dist_km * 0.59) if get_meta('delivery_zone') == 'outside' else 0

    # 5. Insertion en BDD
    success, result = create_order(
        utilisateur_id=session['user_id'],
        cart_items=cart_items,
        prix_menu=total_menus,
        prix_livraison=total_delivery,
        pret_materiel=get_meta('pret_materiel'),
        adresse_livraison=get_meta('adresse_livraison'),
        ville_livraison=get_meta('ville_livraison'),
        code_postal_livraison=get_meta('code_postal_livraison'),
        date_prestation=get_meta('date_prestation'),
        heure_livraison=get_meta('heure_livraison')
    )

    if success:
        user = get_user_by_id(session['user_id'])
        if user and user.get('email'):
            montant_total_paye = total_menus + total_delivery

            total_remise = sum(item.get('remise', 0) for item in cart_items)
            sous_total_brut = sum(item.get('prix_brut', item['total_price']) for item in cart_items)

            valeur_pret = str(get_meta('pret_materiel')).lower()
            pret_materiel_demande = valeur_pret in ['true', 'on', '1', 'yes']

            adresse_complete = f"{get_meta('adresse_livraison')}, {get_meta('code_postal_livraison')} {get_meta('ville_livraison')}"

            send_html_email(
                subject=f"Confirmation de commande - {result}",
                recipient=user['email'],
                template_name="emails/order_confirmation.html",
                prenom=user.get('prenom', 'Gourmet'),
                reference=result,
                cart_items=cart_items,
                sous_total=sous_total_brut,
                remise=total_remise,
                frais_livraison=total_delivery,
                total_paye=montant_total_paye,
                pret_materiel=pret_materiel_demande,
                adresse=adresse_complete
            )

        session.pop('panier', None)
        session.pop('checkout_options', None)
        return render_template('success.html', reference=result)
    else:
        flash("Erreur lors de l'enregistrement : " + result, "error")
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

    # Récupère les commandes de base
    commandes_raw = get_user_orders(session['user_id'])

    # Pour chaque commande, on va chercher ses menus
    commandes_completes = []
    for cmd in commandes_raw:
        # C'EST ICI QU'IL FAUT AJOUTER session['user_id']
        cmd['details'] = get_order_details(cmd['commande_id'], session['user_id'])
        commandes_completes.append(cmd)

    return render_template('my_orders.html', commandes=commandes_completes)

# ROUTE ANNULATION COMMANDE
@app.route('/cancel-order', methods=['POST'])
def client_cancel_order():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    commande_id = request.form.get('commande_id')
    user_id = session['user_id']

    success = cancel_client_order(commande_id, user_id)
    if success:
        flash("Votre commande a bien été annulée.", "success")
    else:
        flash("Impossible d'annuler cette commande. Elle est peut-être déjà prise en charge.", "error")

    return redirect(url_for('my_orders'))

# ROUTE AVIS CLIENT
@app.route('/submit-review', methods=['POST'])
def client_submit_review():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    menu_id = request.form.get('menu_id')
    commande_id = request.form.get('commande_id') # NOUVEAU
    note = request.form.get('note')
    commentaire = request.form.get('commentaire')
    user_id = session['user_id']

    if not menu_id or not commande_id or not note or not commentaire:
        flash("Tous les champs sont obligatoires.", "error")
        return redirect(url_for('my_orders'))

    # On passe le commande_id à la fonction !
    success = add_client_review(user_id, menu_id, commande_id, int(note), commentaire)

    if success:
        flash("Merci ! Votre avis a bien été transmis et est en attente de modération.", "success")
    else:
        flash("Vous avez déjà laissé un avis pour ce menu dans cette commande.", "error")

    return redirect(url_for('my_orders'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # 1. Vérification de la session (méthode de ton projet)
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour accéder à votre profil.", "error")
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    # 2. Si le formulaire est soumis (POST)
    if request.method == 'POST':
        prenom = request.form.get('prenom')
        nom = request.form.get('nom')
        telephone = request.form.get('telephone')
        adresse = request.form.get('adresse')
        ville = request.form.get('ville')
        code_postal = request.form.get('code_postal')
        pays = request.form.get('pays', 'France')

        # Mise à jour en BDD
        success = update_user_profile(user_id, prenom, nom, telephone, adresse, ville, code_postal, pays)

        if success:
            # MAJ de la session au cas où le prénom affiché dans le menu change
            session['user_prenom'] = prenom
            session['user_nom'] = nom
            session.modified = True
            flash("Votre profil a été mis à jour avec succès !", "success")
        else:
            flash("Erreur technique lors de la mise à jour de votre profil.", "error")

        return redirect(url_for('profile'))

    # 3. Affichage de la page (GET)
    current_user = get_user_by_id(user_id)
    if not current_user:
        return redirect(url_for('logout'))

    return render_template('profile.html', user=current_user)
@app.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for('login_page'))


# ==========================================================================
# ESPACE EMPLOYÉ & ADMINISTRATEUR
# ==========================================================================

@app.route('/employee/dashboard')
def employee_dashboard():
    # 1. Sécurité : Vérifier si l'utilisateur est bien connecté
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour accéder à cet espace.", "error")
        return redirect(url_for('login_page', next=request.path))

    # 2. Sécurité : Vérifier si l'utilisateur est un employé (2) ou un admin (1)
    if session.get('user_role') not in [1, 2]:
        flash("Accès refusé. Cet espace est réservé au personnel de Vite & Gourmand.", "error")
        return redirect(url_for('home'))

    # 3. Si c'est bon, on affiche le tableau de bord
    return render_template('employee/dashboard.html')


@app.route('/employee/reviews')
def employee_reviews():
    # Sécurité : réservé au personnel
    if 'user_id' not in session or session.get('user_role') not in [1, 2]:
        flash("Accès refusé.", "error")
        return redirect(url_for('home'))

    connection = get_connection()
    try:
        with connection.cursor(dictionary=True) as cursor:
            # On récupère les avis en attente avec le nom du client et le titre du menu
            sql = """
                  SELECT a.avis_id, \
                         a.note, \
                         a.commentaire, \
                         a.date_avis,
                         u.prenom, \
                         u.nom, \
                         m.titre_menu
                  FROM avis a
                           JOIN utilisateur u ON a.utilisateur_id = u.utilisateur_id
                           JOIN menu m ON a.menu_id = m.menu_id
                  WHERE a.statut_avis = 'En attente'
                  ORDER BY a.date_avis DESC \
                  """
            cursor.execute(sql)
            avis_en_attente = cursor.fetchall()
    finally:
        connection.close()

    return render_template('employee/reviews.html', avis_list=avis_en_attente)


@app.route('/employee/reviews/<int:avis_id>/<string:action>', methods=['POST'])
def handle_review_action(avis_id, action):
    if 'user_id' not in session or session.get('user_role') not in [1, 2]:
        return "Accès interdit", 403

    # Détermination du nouveau statut
    nouveau_statut = 'Validé' if action == 'approve' else 'Refusé'

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE avis SET statut_avis = %s WHERE avis_id = %s"
            cursor.execute(sql, (nouveau_statut, avis_id))
        connection.commit()

        if nouveau_statut == 'Validé':
            flash("L'avis a été approuvé et est maintenant visible sur la page d'accueil !", "success")
        else:
            flash("L'avis a été refusé et masqué.", "success")

    finally:
        connection.close()

    return redirect(url_for('employee_reviews'))

# ==========================================================================
#                       MOT DE PASSE
# ==========================================================================


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        # Vérifier si l'email existe en base
        if email_exists(email):
            # Génère le lien cliquable absolu vers la route reset_password
            reset_url = url_for('reset_password', email=email, _external=True)

            # Envoi de l'e-mail
            send_html_email(
                subject="Réinitialisation de votre mot de passe - Vite & Gourmand",
                recipient=email,
                template_name="emails/email_reset_password.html",
                reset_url=reset_url
            )

        # Message de sécurité global
        flash("Si cette adresse existe, un e-mail de réinitialisation vous a été envoyé.", "success")
        return redirect(url_for('login_page'))

    return render_template('auth/forgot_password.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    # 1. Récupération de l'email soit de l'URL (GET) soit du champ caché du formulaire (POST)
    email = request.args.get('email') or request.form.get('email')

    if not email:
        flash("Lien de réinitialisation invalide ou expiré.", "error")
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Vérification de la correspondance des mots de passe
        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "error")
            return render_template('auth/reset_password.html', email=email)

        # Validation des critères de sécurité du mot de passe
        if not validate_password(new_password):
            flash("Le mot de passe ne respecte pas les critères de sécurité.", "error")
            return render_template('auth/reset_password.html', email=email)

        # Mise à jour sécurisée en Base de Données
        db = get_connection()
        if db:
            try:
                import bcrypt  # <-- On s'assure d'importer bcrypt

                # Hachage avec bcrypt ()
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(new_password.strip().encode('utf-8'), salt)

                cursor = db.cursor()
                # Décodage en utf-8 pour insérer proprement dans le VARCHAR de la table MySQL
                cursor.execute("UPDATE utilisateur SET password = %s WHERE email = %s",
                               (hashed_password.decode('utf-8'), email))
                db.commit()

                flash("Votre mot de passe a bien été réinitialisé. Vous pouvez vous connecter.", "success")
                return redirect(url_for('login_page'))
            except Exception as e:
                print(f"Erreur SQL lors du reset password : {e}")
                flash("Une erreur technique est survenue.", "error")
            finally:
                db.close()
        else:
            flash("Connexion à la base de données impossible.", "error")

    return render_template('auth/reset_password.html', email=email)

if __name__ == '__main__':
    app.run(debug=True, port=5000)