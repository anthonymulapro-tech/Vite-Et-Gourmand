/* FICHIER JS PRINCIPAL - VITE & GOURMAND */

/* 1. INITIALISATION DE LA PAGE */
document.addEventListener("DOMContentLoaded", function () {

    /* 2. COMPARAISON DES MOTS DE PASSE (FORMULAIRE D'INSCRIPTION) */
    const registerForm = document.getElementById('registerForm');

    if (registerForm) {
        registerForm.addEventListener('submit', function (event) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');

            /* Si les deux mots de passe saisis ne sont pas identiques */
            if (password.value !== confirmPassword.value) {
                /* Bloque l'envoi du formulaire au serveur Python */
                event.preventDefault();

                /* Ajout de la classe d'erreur visuelle de Bootstrap sur le champ */
                confirmPassword.classList.add('is-invalid');

                /* Alerte d'avertissement temporaire pour l'utilisateur */
                alert("Les mots de passe ne correspondent pas !");
            } else {
                /* Enlève la classe d'erreur si l'utilisateur a corrigé sa saisie */
                confirmPassword.classList.remove('is-invalid');
            }
        });
    }

    /* 3. VALIDATION GÉNÉRALE DES FORMULAIRES (VISUELS BOOTSTRAP) */
    const forms = document.querySelectorAll('.needs-validation');

    /* Associe un écouteur d'événement à la soumission de chaque formulaire trouvé */
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            /* Si un ou plusieurs champs obligatoires sont vides ou mal remplis */
            if (!form.checkValidity()) {
                /* Empêche l'envoi des données au serveur */
                event.preventDefault();
                /* Bloque la propagation de l'événement dans le DOM */
                event.stopPropagation();
            }

            /* Ajout de la classe qui active les contours verts (valides) et rouges (invalides) */
            form.classList.add('was-validated');
        }, false);
    });

    /* 4. AFFICHAGE / MASQUAGE DES MOTS DE PASSE (BOUTON ŒIL) */
    const toggleButtons = document.querySelectorAll('.toggle-password');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            /* On cible l'input text/password situé juste avant le bouton dans l'input-group */
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');

            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    /* Remplace l'icône de l'œil ouvert par l'œil barré */
                    icon.classList.replace('bi-eye', 'bi-eye-slash');
                } else {
                    input.type = 'password';
                    /* Remplace l'icône de l'œil barré par l'œil ouvert */
                    icon.classList.replace('bi-eye-slash', 'bi-eye');
                }
            }
        });
    });

    /* 5. GESTION DES DOUBLE SLIDERS (FOURCHETTES PRIX ET CONVIVES - PAGE MENUS) */

    /* Fonction interne pour mettre à jour la piste colorée et les textes */
    function initDoubleSlider(minId, maxId, trackId, valueId, unit) {
        const minInput = document.getElementById(minId);
        const maxInput = document.getElementById(maxId);
        const track = document.getElementById(trackId);
        const valDisplay = document.getElementById(valueId);

        /* Si l'un des éléments manque sur la page active, arrêt du script pour éviter un crash */
        if (!minInput || !maxInput || !track || !valDisplay) return;

        function updateSlider() {
            let valMin = parseInt(minInput.value);
            let valMax = parseInt(maxInput.value);

            /* Sécurité anti-croisement : empêche le curseur Min de dépasser le curseur Max */
            if (valMin >= valMax) {
                minInput.value = valMax - parseInt(minInput.step || 1);
                valMin = parseInt(minInput.value);
            }

            /* Calcul des pourcentages pour colorer l'espace entre les deux poignées */
            const minPercent = ((valMin - minInput.min) / (minInput.max - minInput.min)) * 100;
            const maxPercent = ((valMax - maxInput.min) / (maxInput.max - maxInput.min)) * 100;

            /* Injection du dégradé linéaire CSS dynamique */
            track.style.background = `linear-gradient(to right, 
                var(--brand-peach) ${minPercent}%, 
                var(--brand-brown) ${minPercent}%, 
                var(--brand-brown) ${maxPercent}%, 
                var(--brand-peach) ${maxPercent}%)`;

            /* Mise à jour du texte indicateur de la fourchette */
            if (unit === '€') {
                valDisplay.innerText = `${valMin}€ - ${valMax}€`;
            } else {
                valDisplay.innerText = `${valMin} - ${valMax} pers.`;
            }
        }

        /* Mouvements de l'utilisateur sur les deux curseurs */
        minInput.addEventListener('input', updateSlider);
        maxInput.addEventListener('input', updateSlider);

        /* Premier rendu obligatoire pour initialiser les couleurs au chargement */
        updateSlider();
    }

    /* Sécurité : initialisation des curseurs uniquement si le composant est présent dans la page */
    if (document.getElementById('price-min')) {
        initDoubleSlider('price-min', 'price-max', 'price-track', 'price-val', '€');
        initDoubleSlider('people-min', 'people-max', 'people-track', 'people-val', 'pers');
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const display = document.getElementById("total-price-display");
    // SI l'élément n'existe pas sur cette page, on arrête tout de suite !
    if (!display) return;
    const selector = document.querySelector(".custom-quantity-selector");
    const input = document.getElementById("quantity-input");


    // Récupération des règles depuis les data-attributes
    const unitPrice = parseFloat(display.getAttribute("data-unit-price"));
    const minVal = parseInt(display.getAttribute("data-min-convives"));
    const seuilRemise = parseInt(display.getAttribute("data-seuil-remise")); // ex: 5
    const pctRemise = parseInt(display.getAttribute("data-pct-remise")) / 100; // ex: 0.10

    function updatePrice() {
    const qty = parseInt(input.value) || minVal;
    const badge = document.getElementById("discount-badge");
    let total = qty * unitPrice;

    // 1. Logique de remise
    if (qty >= (minVal + seuilRemise)) {
        total = total * (1 - pctRemise);
        badge.innerHTML = `<span style="color: var(--brand-brown);">Remise de ${Math.round(pctRemise * 100)}% appliquée !</span>`;
    } else {
        badge.innerHTML = "";
    }

    // 2. Préparation du prix formaté
    const formattedPrice = total.toFixed(2).replace('.', ',');

    // 3. Mise à jour de l'affichage
    display.innerHTML = `${formattedPrice}€ <span class="fs-6 fw-normal" style="color: var(--brand-brown) !important; opacity: 0.7;">TTC total</span>`;
}

    // --- Gestion du compteur (récupération de ton code précédent) ---
    let timer;
    function startRepeat(delta) {
        let val = parseInt(input.value) || minVal;
        val += delta;
        if (val < minVal) val = minVal;
        input.value = val;
        updatePrice();

        timer = setTimeout(() => {
            timer = setInterval(() => {
                let v = parseInt(input.value) + delta;
                if (v >= minVal) {
                    input.value = v;
                    updatePrice();
                }
            }, 100);
        }, 500);
    }

    function stopRepeat() { clearInterval(timer); clearTimeout(timer); }

    // Événements boutons
    document.querySelector(".btn-plus").addEventListener("mousedown", () => startRepeat(1));
    document.querySelector(".btn-minus").addEventListener("mousedown", () => startRepeat(-1));
    window.addEventListener("mouseup", stopRepeat);

    // Événement saisie manuelle
    input.addEventListener("input", updatePrice);
    input.addEventListener("change", function() {
        if (this.value < minVal) this.value = minVal;
        updatePrice();
    });
    // Initialisation au chargement
    updatePrice();
});

document.addEventListener('DOMContentLoaded', function() {
    const subtotalElement = document.getElementById('display_subtotal');
    const discountElement = document.getElementById('display_discount');

    if (!subtotalElement) return;

    // Récupération des valeurs calculées par Python depuis l'HTML
    const baseSubtotal = parseFloat(subtotalElement.textContent) || 0;
    const baseDiscount = discountElement ? parseFloat(discountElement.textContent) : 0;

    const deliveryZone = document.getElementById('delivery_zone');
    const distanceContainer = document.getElementById('distance_container');
    const distanceKm = document.getElementById('distance_km');
    const displayDelivery = document.getElementById('display_delivery');
    const displayGrandTotal = document.getElementById('display_grand_total');

    function calculateTotal() {
        let deliveryCost = 0;
        // Le total TTC est le Sous-total - Remise
        let finalTotal = baseSubtotal - baseDiscount;

        // 2. Gestion de la livraison
        if (deliveryZone.value === 'outside') {
            distanceContainer.classList.remove('d-none');
            let km = parseFloat(distanceKm.value) || 0;
            if (km > 0) {
                deliveryCost = 5 + (km * 0.59);
            } else {
                deliveryCost = 5;
            }
        } else {
            distanceContainer.classList.add('d-none');
            distanceKm.value = 0;
        }

        displayDelivery.textContent = deliveryCost.toFixed(2);
        finalTotal += deliveryCost;

        // 3. Mise à jour du Total TTC
        displayGrandTotal.textContent = finalTotal.toFixed(2);
    }

    const btnDistMinus = document.getElementById('btn_dist_minus');
    const btnDistPlus = document.getElementById('btn_dist_plus');

    if (btnDistMinus && btnDistPlus) {
        btnDistMinus.addEventListener('click', function() {
            let currentVal = parseInt(distanceKm.value) || 0;
            if (currentVal > 0) {
                distanceKm.value = currentVal - 1;
                calculateTotal(); // Met à jour le prix immédiatement
            }
        });

        btnDistPlus.addEventListener('click', function() {
            let currentVal = parseInt(distanceKm.value) || 0;
            distanceKm.value = currentVal + 1;
            calculateTotal(); // Met à jour le prix immédiatement
        });
    }

    deliveryZone.addEventListener('change', calculateTotal);
    distanceKm.addEventListener('input', calculateTotal);

    // --- GESTION DU MENU DÉROULANT CUSTOM (Zone de livraison) ---
    const dropdownItems = document.querySelectorAll('.custom-delivery-dropdown .dropdown-item');
    const selectedZoneText = document.getElementById('selected-zone-text');

    if (dropdownItems.length > 0) {
        dropdownItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();

                // 1. Change le texte affiché sur le bouton
                selectedZoneText.textContent = this.textContent;

                // 2. Change la valeur de l'input caché
                deliveryZone.value = this.getAttribute('data-value');

                // 3. Déclenche manuellement l'événement 'change' pour forcer le recalcul des frais
                deliveryZone.dispatchEvent(new Event('change'));
            });
        });
    }


    calculateTotal();
});

// --- GESTION DU MENU DÉROULANT CUSTOM (Heure de livraison) ---
    const timeItems = document.querySelectorAll('.time-item');
    const selectedTimeText = document.getElementById('selected-time-text');
    const inputHeureLivraison = document.getElementById('heure_livraison');

    if (timeItems.length > 0 && selectedTimeText && inputHeureLivraison) {
        timeItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();

                // 1. Change le texte affiché sur le bouton
                selectedTimeText.textContent = this.textContent;

                // 2. Change la valeur de l'input caché pour le formulaire
                inputHeureLivraison.value = this.getAttribute('data-value');
            });
        });
    }

    (function () {
    'use strict'

    // Récupère tous les formulaires auxquels on veut appliquer les styles de validation Bootstrap
    var forms = document.querySelectorAll('.needs-validation')

    // Boucle sur chaque formulaire et empêche la soumission si invalide
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    })
})()

// --- GESTION DE LA MODALE DE L'AVIS CLIENT ---
document.addEventListener('DOMContentLoaded', function () {
    var reviewModal = document.getElementById('reviewModal');

    if (reviewModal) {
        reviewModal.addEventListener('show.bs.modal', function (event) {
            // Bouton qui a déclenché la modale
            var button = event.relatedTarget;

            // 1. Extraction des infos cachées dans le bouton
            var menuId = button.getAttribute('data-menu-id');
            var commandeId = button.getAttribute('data-commande-id');
            var menuTitre = button.getAttribute('data-menu-titre');

            // 2. Ciblage des champs de la modale HTML
            var inputMenuId = reviewModal.querySelector('#modal_menu_id');
            var inputCommandeId = reviewModal.querySelector('#modal_commande_id');
            var inputMenuTitre = reviewModal.querySelector('#modal_menu_titre');

            // 3. Injection des valeurs dans la modale
            if (inputMenuId && inputMenuTitre) {
                inputMenuId.value = menuId;
                inputMenuTitre.value = menuTitre; // C'est cette ligne qui fait apparaître le texte !
            }
            if (inputCommandeId) {
                inputCommandeId.value = commandeId;
            }

            // 4. Nettoyage (Reset) pour ne pas garder l'ancien commentaire
            var commentInput = reviewModal.querySelector('#review_comment');
            if (commentInput) {
                commentInput.value = '';
            }

            var noteSelect = reviewModal.querySelector('#review_note');
            if (noteSelect) {
                noteSelect.value = '5';
            }
        });
    }
});

/* ==========================================================================
   6. GESTION DYNAMIQUE DU DROPDOWN STATUT ET CHECKBOX (SUIVI DES COMMANDES)
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function() {
    const statusLinks = document.querySelectorAll('.status-link');

    if (statusLinks.length === 0) return; // Sécurité

    statusLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetValue = this.getAttribute('data-value');
            const orderId = this.getAttribute('data-order-id');

            // 1. Met à jour la valeur de l'input caché pour le serveur Python
            document.getElementById(`input_status_${orderId}`).value = targetValue;

            // 2. Met à jour le texte du bouton visible
            const dropdownBtn = document.getElementById(`dropdownMenuButton_${orderId}`);
            dropdownBtn.textContent = targetValue;

            // 3. Logique dynamique de la checkbox matériel
            const checkbox = document.getElementById(`rest_Check_${orderId}`);
            if (!checkbox) return;

            if (targetValue === 'Terminée') {
                checkbox.disabled = false;
            } else {
                checkbox.disabled = true;
                checkbox.checked = false;
            }
        });
    });
});

/* ==========================================================================
   7. GESTION DYNAMIQUE DU DROPDOWN ÉTAT (GESTION DES HORAIRES EMPLOYÉ)
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function() {
    const scheduleLinks = document.querySelectorAll('.schedule-link');

    if (scheduleLinks.length === 0) return;

    scheduleLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetValue = this.getAttribute('data-value');
            const targetLabel = this.getAttribute('data-label');
            const horaireId = this.getAttribute('data-horaire-id');

            // 1. Met à jour la valeur de l'input caché pour le serveur Python
            document.getElementById(`input_schedule_${horaireId}`).value = targetValue;

            // 2. Met à jour le texte du bouton visible (Ouvert ou Fermé)
            const dropdownBtn = document.getElementById(`dropdownScheduleButton_${horaireId}`);
            dropdownBtn.textContent = targetLabel;
        });
    });
});