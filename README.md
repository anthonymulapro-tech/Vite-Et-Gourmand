# Vite-Et-Gourmand
Projet d'évaluation (ECF) : Application de gestion pour un traiteur événementiel permettant la personnalisation de menus selon des thèmes et des régimes alimentaires.

# Aperçu du Projet

## Design Desktop & Mobile

<img src="docs/img/desktop_page_menus_preview.png" width="800" alt="Maquette Desktop Menu">
<br>
<img src="docs/img/mobile_page_accueil_preview.png" width="300" alt="Maquette Mobile Accueil">

## Conception de la Base de Données (MCD)

<img src="docs/img/mcd_preview.png" width="700" alt="Modèle Conceptuel de Données">

## Stack Technique
- [x] **Conception** : _Draw.io_ (UML/MCD)
- [x] **Design** : _Balsamiq_ (Wireframes)
- [x] **Design** : _Figma_ (Maquettes et charte)
- [x] **Base de données** : _MySQL_ (Structure initiale déployée)
- [X] **Backend** : _Python & Flask_ (Routage dynamique, gestion des sessions et logique métier)
- [X] **Frontend** : _HTML / CSS / Bootstrap / JS_ (Intégration fluide et responsive)
- [ ] **NoSQL** : _MongoDB_ (À venir)

## Documentation Technique
- **UML & MCD** : `/docs/conception_technique/`
- **Design & Wireframes** : `/docs/design_maquettes/` et `/docs/wireframes/`

## Fonctionnalités & Sécurité Implémentées

Le système d'authentification a été conçu en respectant les standards de sécurité actuels et en optimisant l'expérience utilisateur (UX) :

* **Hachage des mots de passe** : Utilisation de la bibliothèque `Bcrypt` côté backend. Aucun mot de passe n'est stocké en clair en base de données (salage et hachage dynamique).
* **Double validation des formulaires** :
  * **Côté Client** : Validation immédiate en HTML5/JS (Regex pour mot de passe fort, format de téléphone à 10 chiffres, emails valides) pour un retour utilisateur instantané sans rechargement de page.
  * **Côté Serveur** : Double vérification de sécurité en Python (`app.py`) pour bloquer les requêtes malveillantes qui contourneraient le navigateur.
* **Gestion intelligente des doublons** : Avant l'inscription, le backend vérifie l'unicité de l'adresse email. En cas de doublon, un message d'erreur ciblé est affiché directement sur le champ concerné sans recharger ni vider les autres saisies de l'utilisateur (grâce à Jinja2).
* **Fidélité de la Charte Graphique** : Surcharge CSS des comportements natifs de Google Chrome (`-webkit-autofill`) et de Bootstrap (`:focus`) pour conserver les tons et le style visuel du site en toutes circonstances.

## Installation et Déploiement Local

* **Prérequis Serveur local** : _Laragon_ (recommandé) ou WAMP/XAMPP.

* **Environnement** :  `Python 3.13`

* **Git** : Clonage du dépôt 

```bash
git clone https://github.com/anthonymulapro-tech/Vite-Et-Gourmand.git
cd Vite-Et-Gourmand
```

#### 1. Configuration de la Base de Données (MySQL)
* a. Ouvrir votre outil de gestion SQL (_HeidiSQL_ ou _phpMyAdmin_ via _Laragon_).
* b. Créer une nouvelle base de données nommée **vite_et_gourmand**.
* c. Importer et exécuter le script de création des tables : `sql/01_create_tables.sql`
* d. Exécuter le script d'insertion des données : `sql/02_insert_data.sql`.

### 2. Configuration des variables d'environnement
Dupliquez le fichier `.env.example` à la racine du projet et renommez-le en `.env`, puis ajustez vos accès si nécessaire :
```bash
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=
DB_NAME=vite_et_gourmand
```

#### 3. Configuration du Backend (Python)
* a. Créer un environnement virtuel : 
```bash 
python -m venv .venv
```

* b. Activer l'environnement : 
  * Windows : 
  ```bash 
  .\.venv\Scripts\activate
  ```
  
  * Linux : 
  ```bash
  source .venv/bin/activate
  ```
  
* c. Installer les dépendances : 
```bash
pip install -r requirements.txt
```

### 4. Serveur Flask
* démarrage du serveur : 
```bash
python app.py
```
Le serveur sera disponible en local sur : http://127.0.0.1:5000

### 5. Liens d'accès aux pages
* a. Page d'accueil : http://127.0.0.1:5000
* b. Inscription : http://127.0.0.1:5000/register
* c. Connexion : http://127.0.0.1:5000/login
