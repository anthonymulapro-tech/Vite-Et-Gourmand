USE vite_et_gourmand;

-- 1. NETTOYAGE COMPLET (Ordre Enfant -> Parent)

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE plat_allergene;
TRUNCATE TABLE menu_plat;
TRUNCATE TABLE photo_menu;
TRUNCATE TABLE avis;
TRUNCATE TABLE commande_menu;
TRUNCATE TABLE commande;
TRUNCATE TABLE plat;
TRUNCATE TABLE menu;
TRUNCATE TABLE utilisateur;
TRUNCATE TABLE role;
TRUNCATE TABLE theme;
TRUNCATE TABLE regime;
TRUNCATE TABLE allergene;
TRUNCATE TABLE horaire;
TRUNCATE TABLE message_contact;
SET FOREIGN_KEY_CHECKS = 1;

-- 2. TABLES MÈRES (Référentiels)

-- a. Rôles
INSERT INTO role (nom_role) VALUES ('administrateur'), ('employé'), ('utilisateur');

-- b. Thèmes
INSERT INTO theme (nom_theme) VALUES ('Noël'), ('Pâques'), ('Évènement'), ('Classique');

-- c. Régimes
INSERT INTO regime (nom_regime) VALUES ('Végétarien'), ('Végan'), ('Classique');

-- d. Allergènes
INSERT INTO allergene (nom_allergene) VALUES
('Gluten'), ('Lactose'), ('Fruits à coque'), ('Œuf'), ('Poisson'), ('Moutarde');

-- e. Horaires
INSERT INTO horaire (jour, heure_midi_ouverture, heure_midi_fermeture, heure_soir_ouverture, heure_soir_fermeture, est_ouvert ) VALUES
('Lundi', NULL, NULL, NULL, NULL, FALSE),-- Fermé
('Mardi', NULL, NULL, NULL, NULL, FALSE),-- Fermé
('Mercredi', '11:00:00', '14:30:00', '18:30:00', '22:00:00', TRUE),
('Jeudi', '11:00:00', '14:30:00','18:30:00', '22:00:00', TRUE),
('Vendredi', '11:00:00', '14:30:00','18:30:00', '22:00:00', TRUE),
('Samedi', '11:00:00', '14:30:00','18:30:00', '22:00:00', TRUE),
('Dimanche', '11:00:00', '14:30:00','18:30:00', '22:00:00', TRUE);

-- 3. UTILISATEURS (José, Employé et Clients)

-- a. Admin (José)
INSERT INTO utilisateur (nom, prenom, telephone, email, password, adresse, ville, code_postal, role_id,  est_actif)
VALUES ('Pascoli', 'José', '0600000000', 'jose.pascoli@viteetgourmand.fr', '$2b$12$LX/fWpoSSWFl.DYMWVPB4ODZLsRdxNiGjLRaxeDvngccnhrdZ1pz2', '10 Rue du Palais', 'Bordeaux', '33000', 1, TRUE);

-- b. Admin (Julie)
INSERT INTO utilisateur (nom, prenom, telephone, email, password, adresse, ville, code_postal, role_id,  est_actif)
VALUES ('Pascoli', 'Julie', '0600000001', 'julie.pascoli@viteetgourmand.fr', '$2b$12$Dp.BxRHQLL8XusFoWLkAXeu526XDiRlbkxCjeCeSa051GNbS8tUKu','10 Rue du Palais', 'Bordeaux', '33000', 1, TRUE);

-- c. Employé (Nassim)
INSERT INTO utilisateur (nom, prenom, telephone, email, password, adresse, ville, code_postal, role_id,  est_actif)
VALUES ('Amir', 'Nassim', '0600000002', 'nassim.amir@viteetgourmand.fr', '$2b$12$D94BqCUXqNrRxvCZ0LXYiOM/2yHxLyEsQK1ZD8iQmqvAb.cwN3GYi', '5 Avenue de la Marne','Bordeaux', '33000', 2, TRUE);

-- d. Marcel (Ancien employé)
INSERT INTO utilisateur (nom, prenom, telephone, email, password, adresse, ville, code_postal, role_id,  est_actif)
VALUES ('Dupont', 'Marcel', '0600000003', 'jean.dupont@viteetgourmand.fr', '$2b$12$QLmsW9ShpWu4aGKkBo.dDujV9lLh.vPHhf1a/GRWHgg2fNemmICmy', '56 Place des Jacobins','Bordeaux', '33000', 2, FALSE);

-- e. Clients (Bernard, Jean, Sophie, Marie, Antoine)
INSERT INTO utilisateur (nom, prenom, telephone, email, password, adresse, ville, code_postal, role_id,  est_actif) VALUES
('Lebrun', 'Bernard', '0622334455', 'bernard.lebrun@orange.fr', '$2b$12$Vg2418/I5vDrXlSYCZ54oO.vqG20bLVSb3daywDz9uKJNmmNpB.ma', '12 Rue Neuve','Bordeaux', '33000', 3, TRUE),
('Aftis', 'Jean', '0633445566', 'jean.aftis@outlook.fr', '$2b$12$zObGXBgzAiwyRAOHO1kvXOhbhqcrybpD9DADHJllhalOJSoqk.ys.', '2 Bis Rue Messimy','Bordeaux', '33000', 3, TRUE),
('Petit', 'Sophie', '0644556677', 'sophie.petit@gmail.com', '$2b$12$gsLXCwuz5pzki2UF.dftkuYnGBQ/dU7cMWsu3TYhtIv8AHr0FQiCu', '45 Rue des Lilas','Pessac', '33600', 3, TRUE),
('Leroy', 'Marie', '0655667788', 'marie.leroy@gmail.com', '$2b$12$Vh7.CSqPuBololwzviAS5ub0BwHr0en9tcJwO2PzoqW5v9j19KjYe', '25 Avenue des Roseaux','Talence', '33400', 3, TRUE),
('El-Lifah', 'Antoine', '0666778899', 'antoine.el-lifah@hotmail.fr', '$2b$12$wZo9RQ54IJNHHjpDqHsEIePYlMAsrAjz/Ss7QkNBx2XQJkP7dHSVG', '32 Place des platanes','Talence', '33400', 3, TRUE);

-- 4. MENUS

INSERT INTO menu (titre_menu, description_menu, prix_par_personne, nombre_personne_min, conditions, quantite_restante, seuil_reduction, pourcentage_reduction, theme_id, regime_id) VALUES
('Menu Fraîcheur', 'Une escale légère et colorée mettant à l''honneur les produits de saison de notre belle région bordelaise.', 25.00, 15, 'Livrable sous 48h ouvrées', 42, 5, 10,  3, 1),
('Menu Gourmand', 'Une parenthèse généreuse et réconfortante mettant à l''honneur les saveurs authentiques de notre terroir.', 35.00, 10, 'Livrable sous 48h ouvrées', 24, 5, 10, 2, 2),
('Menu Étoilé', 'Découvrez une partition gastronomique de haute volée où chaque produit d''exception est sublimé.', 65.00, 5,'Livrable sous 48h ouvrées', 0, 5,10, 1,  3);

-- 5. PHOTOS MENUS

INSERT INTO photo_menu (url_photo, alt_text, menu_id, ordre_affichage) VALUES
('fraicheur_1.jpg', 'Entrée fraîcheur', 1, 1),
('gourmand_1.jpg', 'Plat terroir', 2, 1),
('etoile_1.jpg', 'Dessert gastronomique', 3, 1);

-- 6. PLATS

-- a. Plats pour le Menu Gourmand (Pâques / Vegan)
INSERT INTO plat (titre_plat, description_plat, categorie, url_photo) VALUES
('Salade César au chèvre miel et figue', 'Entrée fraîcheur signature', 'Entrée', 'salade_cesar.jpg'),
('Carpaccio de saumon citronné', 'Saumon frais et zestes de citron', 'Entrée', 'carpaccio_saumon.jpg'),
('Bruschetta avocat tomates', 'Pain toasté et légumes croquants', 'Plat', 'bruschetta.jpg'),
('Salade de lentille et petit pois frais', 'Accompagnement moutarde à l''ancienne', 'Plat', 'lentille.jpg'),
('Tartelette citron', 'Meringue fondante et crème acidulée', 'Dessert', 'tarte_citron.jpg'),
('Cheesecake framboise', 'Coulis de fruits rouges frais', 'Dessert','cheescake.jpg');

-- b. Plats pour le Menu Gourmand (Pâques / Vegan)
INSERT INTO plat (titre_plat, description_plat, categorie, url_photo) VALUES
('Velouté d''asperges blanches', 'Onctueux et léger, saveurs de saison', 'Entrée','asperge.jpg'),
('Tartare de betterave et pignons de pin', 'Fraîcheur de saison aux herbes folles', 'Entrée','betterave.jpg'),
('Risotto aux morilles et ail des ours', 'Riz arborio crémeux et champignons sauvages','Plat','risotto.jpg'),
('Tofu fumé laqué aux petits légumes', 'Protéine végétale et croquant de jardin', 'Plat','tofu.jpg'),
('Salade de fruits exotiques au basilic', 'Ananas, mangue et passion', 'Dessert','salade_fruit.jpg'),
('Mousse au chocolat noir et aquafaba', 'Onctuosité 100% végétale sans œuf', 'Dessert','mousse_chocolat.jpg');

-- c Plats pour le Menu Étoilé (Noël / Classique)
INSERT INTO plat (titre_plat, description_plat, categorie, url_photo) VALUES
('Foie gras de canard mi-cuit', 'Chutney de figues et pain brioché', 'Entrée','foie_gras.jpg'),
('Saint-Jacques snakées et crème de corail', 'Noix de Saint-Jacques et sauce onctueuse', 'Entrée','saint_jacques.jpg'),
('Chapon rôti aux marrons', 'Volaille d''exception et jus corsé', 'Plat','chapon.jpg'),
('Filet de boeuf en croûte et purée truffée', 'Pièce de bœuf tendre et saveur de truffe', 'Plat','filet_boeuf.jpg'),
('Bûche signature au chocolat noir', 'Ganache intense et croustillant praliné', 'Dessert','buche_chocolat.jpg'),
('Pavlova aux fruits rouges de fête', 'Meringue craquante et chantilly légère', 'Dessert','pavlova.jpg');

-- 7. LIAISONS

-- Liaison complète pour le Menu Fraîcheur (ID1)
INSERT INTO menu_plat (menu_id, plat_id, ordre_affichage_plat) VALUES
(1, 1, 1), (1, 2, 2), -- Les 2 Entrées du Menu 1
(1, 3, 3), (1, 4, 4), -- Les 2 Plats du Menu 1
(1, 5, 5), (1, 6, 6); -- Les 2 Desserts du Menu 1

-- Liaison complète pour le Menu Gourmand (ID2)
INSERT INTO menu_plat (menu_id, plat_id, ordre_affichage_plat) VALUES
(2, 7, 1), (2, 8, 2),  -- Les 2 Entrées du Menu 2
(2, 9, 3), (2, 10, 4),  -- Les 2 Plats du Menu 2
(2, 11, 5), (2, 12, 6);  -- Les 2 Desserts du Menu 2

-- Liaison complète pour le Menu Étoilé (ID3)
INSERT INTO menu_plat (menu_id, plat_id, ordre_affichage_plat) VALUES
(3, 13, 1), (3, 14, 2), -- Les 2 Entrées du Menu 3
(3, 15, 3), (3, 16, 4), -- Les 2 Plats du Menu 3
(3, 17, 5), (3, 18, 6); -- Les 2 Desserts du Menu 3

-- Liaison Plat <-> Allergène
INSERT INTO plat_allergene (plat_id, allergene_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), -- Salade César : Gluten, Lactose, Fruits à coque, Œuf
(2, 5), -- Saumon : Poisson
(3, 1), -- Bruschetta : Gluten
(4, 6), -- Salade lentilles : Moutarde
(5, 1), (5, 4), (5, 2), -- Tartelette : Gluten, Œuf, Lactose
(7, 2), -- Velouté asperges : Lactose (crème)
(8, 3), -- Tartare betterave : Fruits à coque (pignons)
(9, 2), -- Risotto : Lactose (parmesan)
(13, 1), -- Foie gras : Gluten (pain brioché)
(14, 5), -- Saint-Jacques : Poisson/Crustacés
(16, 1), (16, 2); -- Bœuf en croûte : Gluten (croûte), Lactose (purée)

-- 8. COMMANDES FICTIVES (Nécessaires pour lier les avis)

INSERT INTO commande (reference_commande, date_prestation, heure_livraison, nombre_personne, prix_menu, statut_commande, utilisateur_id) VALUES
('CMD-TEST-01', '2026-05-10 12:00:00', '12h00 - 12h30', 5, 325.00, 'Terminée', 5),
('CMD-TEST-02', '2026-05-12 19:30:00', '19h30 - 20h00', 10, 650.00, 'Terminée', 6),
('CMD-TEST-03', '2026-05-15 20:00:00', '20h00 - 20h30', 10, 350.00, 'Terminée', 7),
('CMD-TEST-04', '2026-05-18 12:30:00', '12h30 - 13h00', 30, 750.00, 'Terminée', 8),
('CMD-TEST-05', '2026-05-20 19:00:00', '19h00 - 19h30', 15, 375.00, 'Terminée', 9);

-- 9. LIAISONS COMMANDES ET MENUS (commande_menu)

INSERT INTO commande_menu (commande_id, menu_id, quantite) VALUES
(1, 3, 5),  -- Commande 1 : 5x Menu Étoilé
(2, 3, 10), -- Commande 2 : 10x Menu Étoilé
(3, 2, 10), -- Commande 3 : 10x Menu Gourmand
(4, 1, 30), -- Commande 4 : 30x Menu Fraîcheur
(5, 1, 15); -- Commande 5 : 15x Menu Fraîcheur

-- 10. AVIS CLIENTS (Maintenant liés à une commande spécifique)

INSERT INTO avis (commentaire, note, statut_avis, utilisateur_id, menu_id, commande_id) VALUES
('Livraison à l''heure, très bon et personnel très sympathique, je recommande sans hésitation.', 5, 'Validé', 5, 3, 1),
('Je commanderai à nouveau !', 5, 'Validé', 6, 3, 2),
('Rien à dire, tout était parfait !', 5, 'Validé', 7, 2, 3),
('Nous avons pris le menu fraîcheur pour 30 convives et nous n’avons pas été déçus !', 5, 'Validé', 8, 1, 4),
('Tout était délicieux, un moyen pratique de faire des grands repas de famille.', 5, 'Validé', 9, 1, 5);

-- 11. MESSAGES DE CONTACT
INSERT INTO message_contact (nom_contact, prenom_contact, motif, description_contact, email_contact, est_lu) VALUES
('Mercier', 'Léonie', 'Demande de devis', 'Bonjour, je souhaiterais un devis pour un mariage de 100 personnes en septembre. Merci.', 'leonie.mercier@gmail.com', FALSE),
('Brook', 'Alex','Question allergènes', 'Le menu Gourmand peut-il être adapté sans aucune trace de fruits à coque ?', 'alex.brook@hotmail.fr', TRUE);