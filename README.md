# Vite-Et-Gourmand
Projet réalisé dans le cadre de l'ECF pour le titre de développeur Web. Ce projet couvre l'intégralité du cycle de développement : de la conception (UML/MCD), au design (UI/UX), jusqu'au développement complet du Backend et du Frontend.
# Aperçu du Projet

## Design Desktop & Mobile

<img src="docs/img/desktop_page_menus_preview.png" width="800" alt="Maquette Desktop Menu">
<br>
<img src="docs/img/mobile_page_accueil_preview.png" width="300" alt="Maquette Mobile Accueil">

## Documentation Technique
### Conception de la Base de Données (MCD)

<img src="docs/img/mcd_preview.png" width="700" alt="Modèle Conceptuel de Données">

- **UML & MCD** : `/docs/conception_technique/`
- **Design & Wireframes** : `/docs/design_maquettes/` et `/docs/wireframes/`

## Stack Technique
- [x] **Conception** : _Draw.io_ (UML/MCD)
- [x] **Design** : _Balsamiq_ (Wireframes)
- [x] **Design** : _Figma_ (Maquettes et charte)
- [x] **Base de données** : _MySQL_ (Structure initiale déployée)
- [X] **Backend** : _Python & Flask_ (Routage dynamique, gestion des sessions et logique métier)
- [X] **Frontend** : _HTML / CSS / Bootstrap / JS_ (Intégration fluide et responsive)
- [ ] **NoSQL** : _MongoDB_ (À venir)

### Architecture du Projet
```text
Vite-Et-Gourmand/
├── backend/          # Logique métier, modèles SQL et requêtes
├── frontend/         # Vues et assets (CSS, JS, Images, templates HTML)
├── docs/             # Documentation technique (MCD, UML, Maquettes)
├── sql/              # Scripts de création et d'insertion BDD
├── tests/            # Scripts d'assurance qualité et sécurité
├── app.py            # Point d'entrée de l'application Flask et routes
└── requirements.txt  # Dépendances du projet 
```

## Fonctionnalités
* **Fidélité de la Charte Graphique** : Surcharge CSS des comportements natifs de Google Chrome (`-webkit-autofill`) et de Bootstrap (`:focus`) pour conserver les tons et le style visuel du site en toutes circonstances.
* **Affichage / Masquage dynamique du mot de passe** : Intégration d'un bouton œil interactif géré en JavaScript natif et stylisé en CSS pour s'intégrer harmonieusement à la charte graphique, facilitant la saisie des mots de passe complexes.
* **Catalogue Dynamique :** Affichage des menus depuis la base de données avec gestion des stocks en temps réel.
* **Filtres Avancés :** Recherche multicritères (budget, nombre de convives, thèmes, régimes et allergènes).
* **Tunnel de Commande (Panier) :** * Calcul dynamique des prix selon le nombre de convives.
  * Application automatique de règles métier (ex: seuil de réduction pour commandes volumineuses).
  * Persistance du panier via les sessions Flask.


## Sécurité Implémentées

Le système d'authentification a été conçu en respectant les standards de sécurité actuels et en optimisant l'expérience utilisateur (UX) :

* **Hachage des mots de passe** : Utilisation de la bibliothèque `Bcrypt` côté backend. Aucun mot de passe n'est stocké en clair en base de données (salage et hachage dynamique).
* **Double validation des formulaires** :
  * **Côté Client** : Validation immédiate en HTML5/JS (Regex pour mot de passe fort, format de téléphone à 10 chiffres, emails valides) pour un retour utilisateur instantané sans rechargement de page.
  * **Côté Serveur** : Double vérification de sécurité en Python (`app.py`) pour bloquer les requêtes malveillantes qui contourneraient le navigateur.
* **Gestion intelligente des doublons** : Avant l'inscription, le backend vérifie l'unicité de l'adresse email. En cas de doublon, un message d'erreur ciblé est affiché directement sur le champ concerné sans recharger ni vider les autres saisies de l'utilisateur (grâce à Jinja2).

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
SECRET_KEY=une_cle_secrete_aleatoire_et_ultra_securisee
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

## 6. Comptes de Test (Jeu de données)
Pour faciliter l'évaluation, la base de données est fournie avec plusieurs profils de test :

| Rôle | Email | Mot de passe                             |
| :--- | :--- |:-----------------------------------------|
| **Administrateur** | `jose.pascoli@viteetgourmand.fr` | *`25!Fru1tS&Or@nge!Mar0c!Av3nture!`*     |
| **Employé** | `nassim.amir@viteetgourmand.fr` | *`Nassim33_V&G_2026!`*                   |
| **Client** | `bernard.lebrun@orange.fr` | *`Bern@rd!33`*                           |

### 7. Tests de sécurité automatisés (Assurance Qualité)
Le projet intègre un script de test automatique permettant de vérifier la robustesse du backend face aux contournements des validations du navigateur (ex: scripts malveillants contournant les Regex HTML5).

Pour exécuter le test de sécurité :

Assurez-vous que le serveur Flask tourne toujours dans votre premier terminal (python app.py).

Ouvrez un second terminal, activez votre environnement virtuel .venv, puis exécutez :

```bash
python tests/test_security.py
```
Le script simulera des requêtes HTTP directes et vous affichera un rapport de validation dans la console.
