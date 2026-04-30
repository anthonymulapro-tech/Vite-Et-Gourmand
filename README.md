# Vite-Et-Gourmand
Projet d'évaluation (ECF) : Application de gestion pour un traiteur événementiel permettant la personnalisation de menus selon des thèmes et des régimes alimentaires.

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

### Installation et Déploiement Local

* **Prérequis Serveur local** : _Laragon_ (recommandé) ou WAMP/XAMPP.

* **Environnement** :  `Python 3.13`

#### Configuration de la Base de Données (MySQL)
1. Ouvrir votre outil de gestion SQL (_HeidiSQL_ ou _phpMyAdmin_ via _Laragon_).
2. Créer une nouvelle base de données nommée **vite_et_gourmand**.
3. Importer et exécuter le script de création des tables : `sql/01_create_tables.sql`.
