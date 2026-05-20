-- VITE & GOURMAND - SCRIPT DE CRÉATION

CREATE DATABASE IF NOT EXISTS vite_et_gourmand;
USE vite_et_gourmand;

-- Désactivation des contraintes pour pouvoir supprimer les tables sans erreur

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS message_contact;
DROP TABLE IF EXISTS horaire;
DROP TABLE IF EXISTS role;
DROP TABLE IF EXISTS regime;
DROP TABLE IF EXISTS theme;
DROP TABLE IF EXISTS allergene;
DROP TABLE IF EXISTS plat;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS menu;
DROP TABLE IF EXISTS avis;
DROP TABLE IF EXISTS photo_menu;
DROP TABLE IF EXISTS commande_menu;
DROP TABLE IF EXISTS menu_plat;
DROP TABLE IF EXISTS plat_allergene;

SET FOREIGN_KEY_CHECKS = 1;

-- CRÉATION DES TABLES ( tables isolées en premier )

CREATE TABLE message_contact (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    nom_contact VARCHAR(50) NOT NULL,
    prenom_contact VARCHAR(50) NOT NULL,
    motif VARCHAR(100) NOT NULL,
    description_contact TEXT NOT NULL,
    email_contact VARCHAR(255) NOT NULL,
    date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP,
    est_lu BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB;

CREATE TABLE horaire (
    horaire_id INT AUTO_INCREMENT PRIMARY KEY,
    jour VARCHAR(20) NOT NULL,
    heure_midi_ouverture TIME,
    heure_midi_fermeture TIME,
    heure_soir_ouverture TIME,
    heure_soir_fermeture TIME,
    est_ouvert BOOL DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    nom_role VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE regime (
    regime_id INT AUTO_INCREMENT PRIMARY KEY,
    nom_regime VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE theme (
    theme_id INT AUTO_INCREMENT PRIMARY KEY,
    nom_theme VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE allergene (
    allergene_id INT AUTO_INCREMENT PRIMARY KEY,
    nom_allergene VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE plat (
    plat_id INT AUTO_INCREMENT PRIMARY KEY,
    titre_plat VARCHAR(100) NOT NULL,
    description_plat VARCHAR(255),
    url_photo VARCHAR(255),
    categorie ENUM('Entrée', 'Plat', 'Dessert') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE utilisateur (
    utilisateur_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    telephone VARCHAR(20),
    pays VARCHAR(100) DEFAULT 'France',
    ville VARCHAR(100),
    adresse VARCHAR(255),
    code_postal CHAR(5),
    est_actif BOOL DEFAULT TRUE,
    role_id INT NOT NULL,
    CONSTRAINT fk_utilisateur_role FOREIGN KEY (role_id) REFERENCES role(role_id)
) ENGINE=InnoDB;

CREATE TABLE commande (
    commande_id INT AUTO_INCREMENT PRIMARY KEY,
    reference_commande VARCHAR(30) NOT NULL UNIQUE,
    date_commande DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_prestation DATETIME NOT NULL,
    heure_livraison VARCHAR (50) NOT NULL,
    prix_menu DECIMAL(10,2),
    nombre_personne INT NOT NULL,
    prix_livraison DECIMAL(10,2),
    ville_livraison VARCHAR(100),
    adresse_livraison VARCHAR(255),
    code_postal_livraison CHAR(5),
    statut_commande VARCHAR(50),
    motif_annulation TEXT,
    pret_materiel BOOL DEFAULT FALSE,
    restitution_materiel BOOL DEFAULT FALSE,
    utilisateur_id INT NOT NULL,
    CONSTRAINT fk_commande_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
) ENGINE=InnoDB;

CREATE TABLE menu (
    menu_id INT AUTO_INCREMENT PRIMARY KEY,
    titre_menu VARCHAR(50) NOT NULL,
    description_menu VARCHAR(255),
    nombre_personne_min INT DEFAULT 1,
    prix_par_personne DECIMAL(10,2) NOT NULL,
    conditions VARCHAR(255),
    quantite_restante INT,
    seuil_reduction INT DEFAULT 5,
    pourcentage_reduction INT DEFAULT 10,
    theme_id INT,
    regime_id INT,
    CONSTRAINT fk_menu_theme FOREIGN KEY (theme_id) REFERENCES theme(theme_id),
    CONSTRAINT fk_menu_regime FOREIGN KEY (regime_id) REFERENCES regime(regime_id)
) ENGINE=InnoDB;

CREATE TABLE avis (
    avis_id INT AUTO_INCREMENT PRIMARY KEY,
    note INT NOT NULL,
    commentaire TEXT,
    statut_avis VARCHAR(50) DEFAULT 'En attente',
    date_avis DATETIME DEFAULT CURRENT_TIMESTAMP,
    utilisateur_id INT NOT NULL,
    menu_id INT NOT NULL,
    commande_id INT NOT NULL,
    CONSTRAINT fk_avis_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id),
    CONSTRAINT fk_avis_menu FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
    CONSTRAINT fk_avis_commande FOREIGN KEY (commande_id) REFERENCES commande(commande_id)
) ENGINE=InnoDB;

CREATE TABLE photo_menu (
    photo_menu_id INT AUTO_INCREMENT PRIMARY KEY,
    url_photo VARCHAR(255) NOT NULL,
    alt_text VARCHAR(255) DEFAULT 'Photo du menu',
    ordre_affichage INT DEFAULT 0,
    menu_id INT NOT NULL,
    CONSTRAINT fk_photo_menu_menu FOREIGN KEY (menu_id) REFERENCES menu(menu_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- TABLES DE LIAISON
CREATE TABLE commande_menu (
    commande_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantite INT NOT NULL DEFAULT 1,
    PRIMARY KEY (commande_id, menu_id),
    CONSTRAINT fk_cm_commande FOREIGN KEY (commande_id) REFERENCES commande(commande_id),
    CONSTRAINT fk_cm_menu FOREIGN KEY (menu_id) REFERENCES menu(menu_id)
) ENGINE=InnoDB;

CREATE TABLE menu_plat (
    menu_id INT NOT NULL,
    plat_id INT NOT NULL,
    ordre_affichage_plat INT,
    PRIMARY KEY (menu_id, plat_id),
    CONSTRAINT fk_mp_menu FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
    CONSTRAINT fk_mp_plat FOREIGN KEY (plat_id) REFERENCES plat(plat_id)
) ENGINE=InnoDB;

CREATE TABLE plat_allergene (
    plat_id INT NOT NULL,
    allergene_id INT NOT NULL,
    PRIMARY KEY (plat_id, allergene_id),
    CONSTRAINT fk_pa_plat FOREIGN KEY (plat_id) REFERENCES plat(plat_id),
    CONSTRAINT fk_pa_allergene FOREIGN KEY (allergene_id) REFERENCES allergene(allergene_id)
) ENGINE=InnoDB;


-- OPTIMISATIONS & INDEXATION


-- 1. Index pour accélérer la connexion des utilisateurs (Recherche par email fréquente)
CREATE INDEX idx_utilisateur_email ON utilisateur(email);

-- 2. Index pour optimiser l'affichage de l'historique des commandes d'un client
CREATE INDEX idx_commande_utilisateur ON commande(utilisateur_id);

-- 3. Index pour optimiser le tri et l'affichage des avis modérés sur la page d'accueil
CREATE INDEX idx_avis_statut_date ON avis(statut_avis, date_avis DESC);

-- 4. Index sur les filtres de recherche du catalogue (Thèmes et Régimes)
CREATE INDEX idx_menu_filtres ON menu(theme_id, regime_id);