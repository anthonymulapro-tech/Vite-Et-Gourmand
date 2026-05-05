# Vite-Et-Gourmand
Projet d'évaluation (ECF) : Application de gestion pour un traiteur événementiel permettant la personnalisation de menus selon des thèmes et des régimes alimentaires.

## Aperçu du Projet

### Design Desktop & Mobile

<img src="docs/img/desktop_page_menus_preview.png" width="800" alt="Maquette Desktop Menu">
<br>
<img src="docs/img/mobile_page_accueil_preview.png" width="300" alt="Maquette Mobile Accueil">

### Conception de la Base de Données (MCD)

<img src="docs/img/mcd_preview.png" width="700" alt="Modèle Conceptuel de Données">

### Stack Technique
- [x] **Conception** : _Draw.io_ (UML/MCD)
- [x] **Design** : _Balsamiq_ (Wireframes)
- [x] **Design** : _Figma_ (Maquettes et charte)
- [x] **Base de données** : _MySQL_ (Structure initiale déployée)
- [ ] **Backend** : _Python_ (À venir)
- [ ] **Frontend** : _HTML / CSS / Bootstrap_ (À venir)
- [ ] **NoSQL** : _MongoDB_ (À venir)

### Documentation Technique
- **UML & MCD** : `/docs/conception_technique/`
- **Design & Wireframes** : `/docs/design_maquettes/` et `/docs/wireframes/`

### 0. Installation et Déploiement Local

* **Prérequis Serveur local** : _Laragon_ (recommandé) ou WAMP/XAMPP.

* **Environnement** :  `Python 3.13`

* **Git** : Clonage du dépôt 

git clone https://github.com/anthonymulapro-tech/Vite-Et-Gourmand.git
cd Vite-Et-Gourmand

#### 1. Configuration de la Base de Données (MySQL)
* a. Ouvrir votre outil de gestion SQL (_HeidiSQL_ ou _phpMyAdmin_ via _Laragon_).
* b. Créer une nouvelle base de données nommée **vite_et_gourmand**.
* c. Importer et exécuter le script de création des tables : `sql/01_create_tables.sql`.
* d. Exécuter le script d'insertion des données : `sql/02_insert_data.sql`.

#### 2. Configuration du Backend (Python)
* a. Créer un environnement virtuel : `python -m venv venv`
* b. Activer l'environnement : Windows : `.\venv\Scripts\activate`
* c. Installer les dépendances : `pip install -r requirements.txt`
