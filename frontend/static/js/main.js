/* ==========================================================================
   FICHIER JS PRINCIPAL - VITE & GOURMAND
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================================================
       1. FILTRES DYNAMIQUES ET SLIDERS (PAGE MENUS)
       ========================================================================== */
    const searchInput = document.querySelector('.custom-search-input');

    if (document.querySelector('.menu-card-wrapper')) {

        function applyFilters() {
            if (!searchInput) return;

            const searchVal = searchInput.value.toLowerCase();
            const priceMin = parseFloat(document.getElementById('price-min').value);
            const priceMax = parseFloat(document.getElementById('price-max').value);
            const peopleLimit = parseInt(document.getElementById('people-filter').value);

            const selectedThemes = Array.from(document.querySelectorAll('input[id^="theme-"]:checked')).map(el => el.id.replace('theme-', ''));
            const selectedDiets = Array.from(document.querySelectorAll('input[id^="diet-"]:checked')).map(el => el.id.replace('diet-', ''));
            const selectedAllergies = Array.from(document.querySelectorAll('input[id^="allergy-"]:checked')).map(el => {
                let val = el.id.replace('allergy-', '').toLowerCase();
                if (val === 'noix') return 'fruits à coque';
                return val;
            });

            const cards = document.querySelectorAll('.menu-card-wrapper');

            cards.forEach(card => {
                const titleElement = card.querySelector('.menu-card-title');
                const title = titleElement ? titleElement.innerText.toLowerCase() : "";

                const price = parseFloat(card.getAttribute('data-price'));
                const people = parseInt(card.getAttribute('data-people'));
                const theme = (card.getAttribute('data-theme') || "").toLowerCase();
                const diet = (card.getAttribute('data-diet') || "").toLowerCase();
                const cardAllergies = (card.getAttribute('data-allergies') || "").split(',').map(a => a.trim().toLowerCase());

                const matchesSearch = title.includes(searchVal);
                const matchesPrice = price >= priceMin && price <= priceMax;
                const matchesPeople = people <= peopleLimit;
                const matchesTheme = selectedThemes.length === 0 || selectedThemes.includes(theme);
                const matchesDiet = selectedDiets.length === 0 || selectedDiets.includes(diet);

                const hasForbiddenAllergy = selectedAllergies.some(allergy => cardAllergies.includes(allergy.toLowerCase()));

                if (matchesSearch && matchesPrice && matchesPeople && matchesTheme && matchesDiet && !hasForbiddenAllergy) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        // Écouteurs d'événements pour les filtres
        if (searchInput) searchInput.addEventListener('input', applyFilters);
        document.querySelectorAll('.btn-check').forEach(cb => cb.addEventListener('change', applyFilters));

        // Slider Prix (Double)
        function initDoubleSlider(minId, maxId, trackId, valueId) {
            const minInput = document.getElementById(minId);
            const maxInput = document.getElementById(maxId);
            const track = document.getElementById(trackId);
            const valDisplay = document.getElementById(valueId);
            if (!minInput || !maxInput || !track || !valDisplay) return;

            function updateSlider() {
                let valMin = parseInt(minInput.value);
                let valMax = parseInt(maxInput.value);
                if (valMin >= valMax) { minInput.value = valMax - 5; valMin = parseInt(minInput.value); }
                const minP = ((valMin - minInput.min) / (minInput.max - minInput.min)) * 100;
                const maxP = ((valMax - minInput.min) / (minInput.max - minInput.min)) * 100;
                track.style.background = `linear-gradient(to right, var(--brand-peach) ${minP}%, var(--brand-brown) ${minP}%, var(--brand-brown) ${maxP}%, var(--brand-peach) ${maxP}%)`;
                valDisplay.innerText = `${valMin}€ - ${valMax}€`;
                applyFilters();
            }
            minInput.addEventListener('input', updateSlider);
            maxInput.addEventListener('input', updateSlider);
            updateSlider();
        }
        if (document.getElementById('price-min')) initDoubleSlider('price-min', 'price-max', 'price-track', 'price-val');

        // Slider Convives (Simple)
        const peopleFilter = document.getElementById('people-filter');
        const peopleVal = document.getElementById('people-val');
        const peopleTrack = document.getElementById('people-track');
        if (peopleFilter && peopleTrack) {
            peopleFilter.addEventListener('input', function() {
                peopleVal.innerText = `${this.value} pers.`;
                const p = ((this.value - this.min) / (this.max - this.min)) * 100;
                peopleTrack.style.background = `linear-gradient(to right, var(--brand-brown) ${p}%, var(--brand-peach) ${p}%)`;
                applyFilters();
            });
            peopleTrack.style.background = `linear-gradient(to right, var(--brand-brown) 100%, var(--brand-peach) 100%)`;
        }
    }


    /* ==========================================================================
       2. CALCUL DU PRIX ET QUANTITÉ (PAGE DÉTAIL MENU)
       ========================================================================== */
    const priceDisplay = document.getElementById("total-price-display");

    if (priceDisplay) {
        const selector = document.querySelector(".custom-quantity-selector");
        const qtyInput = document.getElementById("quantity-input");

        const unitPrice = parseFloat(priceDisplay.getAttribute("data-unit-price"));
        const minVal = parseInt(priceDisplay.getAttribute("data-min-convives"));
        const seuilRemise = parseInt(priceDisplay.getAttribute("data-seuil-remise"));
        const pctRemise = parseInt(priceDisplay.getAttribute("data-pct-remise")) / 100;

        function updatePrice() {
            const qty = parseInt(qtyInput.value) || minVal;
            const badge = document.getElementById("discount-badge");
            let total = qty * unitPrice;

            if (qty >= (minVal + seuilRemise)) {
                total = total * (1 - pctRemise);
                badge.innerHTML = `<span style="color: var(--brand-brown);">Remise de ${Math.round(pctRemise * 100)}% appliquée !</span>`;
            } else {
                badge.innerHTML = "";
            }

            const formattedPrice = total.toFixed(2).replace('.', ',');
            priceDisplay.innerHTML = `${formattedPrice}€ <span class="fs-6 fw-normal" style="color: var(--brand-brown) !important; opacity: 0.7;">TTC total</span>`;
        }

        let timer;
        function startRepeat(delta) {
            let val = parseInt(qtyInput.value) || minVal;
            val += delta;
            if (val < minVal) val = minVal;
            qtyInput.value = val;
            updatePrice();

            timer = setTimeout(() => {
                timer = setInterval(() => {
                    let v = parseInt(qtyInput.value) + delta;
                    if (v >= minVal) {
                        qtyInput.value = v;
                        updatePrice();
                    }
                }, 100);
            }, 500);
        }

        function stopRepeat() { clearInterval(timer); clearTimeout(timer); }

        document.querySelector(".btn-plus")?.addEventListener("mousedown", () => startRepeat(1));
        document.querySelector(".btn-minus")?.addEventListener("mousedown", () => startRepeat(-1));
        window.addEventListener("mouseup", stopRepeat);

        qtyInput.addEventListener("input", updatePrice);
        qtyInput.addEventListener("change", function() {
            if (this.value < minVal) this.value = minVal;
            updatePrice();
        });

        updatePrice();
    }


    /* ==========================================================================
       3. GESTION DE LA LIVRAISON ET PANIER (PAGE COMMANDE)
       ========================================================================== */
    const deliveryZone = document.getElementById('delivery_zone');
    const distanceContainer = document.getElementById('distance_container');
    const distanceKm = document.getElementById('distance_km');
    const displayDelivery = document.getElementById('display_delivery');
    const displayGrandTotal = document.getElementById('display_grand_total');

    // FONCTION DE CALCUL DU TOTAL GÉNÉRAL
    function calculateTotal() {
        if (!displayGrandTotal) return;

        // 1. On récupère le sous-total ET la remise directement dans le HTML
        let currentSubtotal = parseFloat(document.getElementById('display_subtotal').textContent) || 0;
        let currentDiscount = parseFloat(document.getElementById('display_discount').textContent) || 0;

        // 2. Le total de départ, c'est le Sous-total MOINS la remise
        let finalTotal = currentSubtotal - currentDiscount;
        let deliveryCost = 0;

        // 3. Calcul des frais de livraison si hors zone
        if (deliveryZone && deliveryZone.value === 'outside') {
            distanceContainer.classList.remove('d-none');
            let km = parseFloat(distanceKm.value) || 0;
            deliveryCost = km > 0 ? 5 + (km * 0.59) : 5;
        } else if (distanceContainer) {
            distanceContainer.classList.add('d-none');
            if (distanceKm) distanceKm.value = 0;
        }

        // 4. Mise à jour des affichages du bloc récapitulatif
        if (displayDelivery) displayDelivery.textContent = deliveryCost.toFixed(2);
        finalTotal += deliveryCost;
        displayGrandTotal.textContent = finalTotal.toFixed(2);
    }

    // Écouteurs pour la livraison (seulement si on est sur la page panier)
    if (deliveryZone) {
        deliveryZone.addEventListener('change', calculateTotal);
        if (distanceKm) distanceKm.addEventListener('input', calculateTotal);

        document.querySelectorAll('.custom-delivery-dropdown .dropdown-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                document.getElementById('selected-zone-text').textContent = this.textContent;
                deliveryZone.value = this.getAttribute('data-value');
                deliveryZone.dispatchEvent(new Event('change'));
            });
        });

        // Les boutons +/- de la distance
        document.getElementById('btn_dist_minus')?.addEventListener('click', () => {
            if (distanceKm.value > 0) { distanceKm.value--; calculateTotal(); }
        });
        document.getElementById('btn_dist_plus')?.addEventListener('click', () => {
            distanceKm.value++; calculateTotal();
        });

        calculateTotal(); // Initialisation au chargement
    }

    // --- FONCTION UTILITAIRE : MISE À JOUR DES TOTAUX DE L'INTERFACE ---
    function updateCartUI(data) {
        // Sous-total et Remise
        const subtotalEl = document.getElementById('display_subtotal');
        if (subtotalEl) subtotalEl.innerText = data.new_subtotal;

        const discountEl = document.getElementById('display_discount');
        if (discountEl) discountEl.innerText = data.new_discount;

        // Grand Total TTC
        const grandTotalEl = document.getElementById('display_grand_total');
        if (grandTotalEl) grandTotalEl.innerText = data.new_subtotal;

        // Affichage/Masquage de la ligne de remise
        const discountRow = document.getElementById('discount_row');
        if (discountRow) {
            if (parseFloat(data.new_discount) > 0) {
                discountRow.classList.remove('d-none');
            } else {
                discountRow.classList.add('d-none');
            }
        }

        // Badges du panier
        const cartBadge = document.getElementById('cart-badge');
        const floatingBadge = document.getElementById('floating-cart-badge');
        if (cartBadge) cartBadge.innerText = data.cart_count;
        if (floatingBadge) floatingBadge.innerText = data.cart_count;
    }

    // --- 1. REQUÊTES ASYNCHRONES POUR LES QUANTITÉS (+ et -) ---
    document.querySelectorAll('.btn-qty').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const idMenu = this.getAttribute('data-id');
            const action = this.getAttribute('data-action');

            fetch('/update-cart-async', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify({ id_menu: idMenu, action: action })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`qty-${idMenu}`).value = data.new_qty;
                    document.getElementById(`line-total-${idMenu}`).innerText = data.new_line_total;
                    updateCartUI(data);
                } else {
                    showToast(data.message, "error");
                }
            })
            .catch(err => console.error("Erreur AJAX:", err));
        });
    });

    // --- 2. GESTION DU MODAL DE SUPPRESSION D'UN MENU ---
    let menuIdToRemove = null;
    let rowToRemove = null;

    // A. Écouter le clic sur les poubelles pour ouvrir le modal
    document.querySelectorAll('.btn-remove-item').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            menuIdToRemove = this.getAttribute('data-id');
            rowToRemove = document.getElementById(`row-${menuIdToRemove}`);

            // Méthode propre et sécurisée pour ouvrir un modal Bootstrap en JS
            const modalElement = document.getElementById('confirmRemoveItemModal');
            const removeModal = bootstrap.Modal.getOrCreateInstance(modalElement);
            removeModal.show();
        });
    });
    // B. Écouter le clic sur le bouton de confirmation DANS le modal
    const btnConfirmRemove = document.getElementById('btn-confirm-remove-item');
    if (btnConfirmRemove) {
        btnConfirmRemove.addEventListener('click', function() {
            if (!menuIdToRemove) return;

            // 1. Masquer le modal proprement
            const modalEl = document.getElementById('confirmRemoveItemModal');
            const modalInst = bootstrap.Modal.getInstance(modalEl);
            if (modalInst) modalInst.hide();

            // 2. Lancer la requête asynchrone
            fetch('/update-cart-async', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify({ id_menu: menuIdToRemove, action: 'remove' })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Si le panier est devenu vide, la page se recharge
                    if (data.cart_empty) {
                        window.location.reload();
                        return;
                    }

                    // A. Suppression immédiate de la ligne
                    if (rowToRemove) {
                        rowToRemove.remove();
                    }

                    // B. message à côté du titre
                    const popMsg = document.getElementById('pop-remove-msg');
                    if (popMsg) {
                        popMsg.classList.remove('d-none');
                        if (window.cartMessageTimeout) clearTimeout(window.cartMessageTimeout);
                        window.cartMessageTimeout = setTimeout(() => {
                            popMsg.classList.add('d-none');
                        }, 3000);
                    }

                    // C. Mise à jour des totaux
                    updateCartUI(data);

                    // D. RESET SÉCURISÉ DES VARIABLES
                    menuIdToRemove = null;
                    rowToRemove = null;

                } else {
                    console.error("Erreur serveur :", data.message);
                }
            })
            .catch(err => console.error("Erreur AJAX fatale :", err));
        });
    }


    /* ==========================================================================
       4. SÉCURITÉ ET FORMULAIRES (INSCRIPTION, CONNEXION)
       ========================================================================== */

    // Comparaison des mots de passe (Inscription)
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function (event) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');

            if (password.value !== confirmPassword.value) {
                event.preventDefault();
                confirmPassword.classList.add('is-invalid');
                alert("Les mots de passe ne correspondent pas !");
            } else {
                confirmPassword.classList.remove('is-invalid');
            }
        });
    }

    // Affichage / Masquage des mots de passe (Bouton Œil)
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function () {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');

            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.replace('bi-eye', 'bi-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.replace('bi-eye-slash', 'bi-eye');
                }
            }
        });
    });

    // Validation globale des formulaires (Visuels Bootstrap)
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });


    /* ==========================================================================
       5. MODALES ET TABLEAUX DE BORD (AVIS, STATUTS, HORAIRES)
       ========================================================================== */

    // Gestion de la modale des avis clients
    const reviewModal = document.getElementById('reviewModal');
    if (reviewModal) {
        reviewModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const menuId = button.getAttribute('data-menu-id');
            const commandeId = button.getAttribute('data-commande-id');
            const menuTitre = button.getAttribute('data-menu-titre');

            const inputMenuId = reviewModal.querySelector('#modal_menu_id');
            const inputCommandeId = reviewModal.querySelector('#modal_commande_id');
            const inputMenuTitre = reviewModal.querySelector('#modal_menu_titre');
            const commentInput = reviewModal.querySelector('#review_comment');
            const noteSelect = reviewModal.querySelector('#review_note');

            if (inputMenuId && inputMenuTitre) {
                inputMenuId.value = menuId;
                inputMenuTitre.value = menuTitre;
            }
            if (inputCommandeId) inputCommandeId.value = commandeId;
            if (commentInput) commentInput.value = '';
            if (noteSelect) noteSelect.value = '5';
        });
    }

    // Gestion du statut des commandes (Dropdown Employé/Admin)
    document.querySelectorAll('.status-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetValue = this.getAttribute('data-value');
            const orderId = this.getAttribute('data-order-id');

            document.getElementById(`input_status_${orderId}`).value = targetValue;
            document.getElementById(`dropdownMenuButton_${orderId}`).textContent = targetValue;

            const checkbox = document.getElementById(`rest_Check_${orderId}`);
            if (checkbox) {
                if (targetValue === 'Terminée') {
                    checkbox.disabled = false;
                } else {
                    checkbox.disabled = true;
                    checkbox.checked = false;
                }
            }
        });
    });

    // Gestion des horaires (Dropdown Employé)
    document.querySelectorAll('.schedule-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetValue = this.getAttribute('data-value');
            const targetLabel = this.getAttribute('data-label');
            const horaireId = this.getAttribute('data-horaire-id');

            document.getElementById(`input_schedule_${horaireId}`).value = targetValue;
            document.getElementById(`dropdownScheduleButton_${horaireId}`).textContent = targetLabel;
        });
    });

/* ==========================================================================
       6. ASYNCHRONE (AJOUT AU PANIER AVEC TOAST BOOTSTRAP)
       ========================================================================== */

    // --- Fonction utilitaire pour afficher une belle notification ---
    function showToast(message, type = 'success') {
        const toastEl = document.getElementById('liveToast');
        const toastMessage = document.getElementById('toast-message');

        if (toastEl && toastMessage) {
            toastMessage.textContent = message;

            // On nettoie les anciennes couleurs
            toastEl.classList.remove('bg-success', 'bg-danger', 'bg-brand-brown');

            // On applique la couleur selon le succès ou l'erreur
            if (type === 'success') {
                toastEl.classList.add('bg-success');
            } else {
                toastEl.classList.add('bg-danger');
            }

            // On lance l'animation Bootstrap
            const toast = new bootstrap.Toast(toastEl, { delay: 3000 }); // Disparaît après 3 secondes
            toast.show();
        } else {
            // Sécurité : si le HTML du Toast est introuvable, on fait un vieux alert
            alert(message);
        }
    }

    // --- Interception du formulaire ---
    const addToCartForm = document.getElementById('add-to-cart-form');

    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(addToCartForm);

            fetch(addToCartForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
               if (data.success) {
                    // 1. Mise à jour de la pastille du menu principal
                    const badge = document.getElementById('cart-badge');
                    if (badge) {
                        badge.innerText = data.cart_count;
                        badge.classList.remove('d-none');

                        badge.classList.add('animate__animated', 'animate__headShake');
                        setTimeout(() => badge.classList.remove('animate__animated', 'animate__headShake'), 1000);
                    }

                    // 2. Mise à jour et affichage du Panier Flottant (Le jumeau)
                    const floatingCart = document.getElementById('floating-cart');
                    const floatingBadge = document.getElementById('floating-cart-badge');

                    if (floatingCart && floatingBadge) {
                        floatingCart.classList.remove('d-none'); // On fait apparaitre le bouton flottant
                        floatingBadge.innerText = data.cart_count; // On met à jour son chiffre

                        // Petit effet de rebond sur le bouton flottant
                        floatingCart.classList.remove('animate__fadeInUp'); // Retire l'animation d'apparition initiale
                        floatingCart.classList.add('animate__animated', 'animate__tada');
                        setTimeout(() => floatingCart.classList.remove('animate__animated', 'animate__tada'), 1000);
                    }

                    // 3. Affichage du message
                    showToast("Le menu a bien été ajouté au panier !", "success");

                } else {
                    // Message d'erreur (en rouge)
                    showToast("Erreur : " + data.message, "error");
                }
            })
            .catch(error => {
                console.error('Erreur :', error);
                showToast("Une erreur technique est survenue.", "error");
            });
        });
    }

    /* ==========================================================================
       7. GESTION DU PANIER FLOTTANT ET TOAST (ÉVITEMENT DU FOOTER)
       ========================================================================== */
    window.addEventListener('scroll', function() {
        const floatingCart = document.getElementById('floating-cart');
        const toastContainer = document.querySelector('.toast-container');
        const footer = document.querySelector('.custom-footer');

        if (footer) {
            const footerRect = footer.getBoundingClientRect();
            const viewportHeight = window.innerHeight;

            // Si le haut du footer entre dans l'écran
            if (footerRect.top < viewportHeight) {
                // Calcul de la marge pour s'arrêter net au-dessus du footer
                const pushAmount = viewportHeight - footerRect.top + 50;

                if (floatingCart) floatingCart.style.bottom = pushAmount + 'px';
                if (toastContainer) toastContainer.style.bottom = pushAmount + 'px';
            } else {
                // Position normale quand le footer n'est pas visible
                if (floatingCart) floatingCart.style.bottom = '50px';
                if (toastContainer) toastContainer.style.bottom = '50px';
            }
        }
    });

   /* ==========================================================================
       VIDAGE DU PANIER EN ASYNC VIA MODAL CUSTOM
       ========================================================================== */
    const btnConfirmClear = document.getElementById('btn-confirm-clear-cart');

    if (btnConfirmClear) {
        btnConfirmClear.addEventListener('click', function() {
            // 1. Fermer le modal Bootstrap programmatiquement
            const modalElement = document.getElementById('confirmClearCartModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();

            // 2. Envoyer la requête Fetch au serveur
            fetch('/clear-cart-async', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    showToast("Une erreur est survenue lors du vidage du panier.", "error");
                }
            })
            .catch(err => console.error("Erreur:", err));
        });
    }

    /* ==========================================================================
       8. ANNULATION ASYNCHRONE DE COMMANDE (ESPACE CLIENT)
       ========================================================================== */
    let orderIdToCancel = null;
    let cancelBoxToHide = null;
    let statusBadgeToUpdate = null;

    document.querySelectorAll('.btn-trigger-cancel-order').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            orderIdToCancel = this.getAttribute('data-id');
            const orderRef = this.getAttribute('data-ref');

            cancelBoxToHide = document.getElementById(`cancel-box-${orderIdToCancel}`);
            statusBadgeToUpdate = document.getElementById(`status-badge-${orderIdToCancel}`);

            const refContainer = document.getElementById('modal-cancel-order-ref');
            if (refContainer) refContainer.innerText = orderRef;

            const cancelModalEl = document.getElementById('confirmCancelOrderModal');
            const cancelModal = bootstrap.Modal.getOrCreateInstance(cancelModalEl);
            cancelModal.show();
        });
    });

    const btnConfirmCancelOrder = document.getElementById('btn-confirm-cancel-order');
    if (btnConfirmCancelOrder) {
        btnConfirmCancelOrder.addEventListener('click', function() {
            if (!orderIdToCancel) return;

            const modalEl = document.getElementById('confirmCancelOrderModal');
            const modalInst = bootstrap.Modal.getInstance(modalEl);
            if (modalInst) modalInst.hide();

            fetch('/client-cancel-order-async', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ commande_id: orderIdToCancel })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (statusBadgeToUpdate) statusBadgeToUpdate.innerText = "Commande annulée";
                    if (cancelBoxToHide) cancelBoxToHide.remove();
                    if (typeof showToast === "function") showToast("La commande a bien été annulée.", "success");

                    orderIdToCancel = null;
                    cancelBoxToHide = null;
                    statusBadgeToUpdate = null;
                } else {
                    if (typeof showToast === "function") showToast(data.message || "Impossible d'annuler cette commande.", "error");
                }
            })
            .catch(err => console.error("Erreur d'annulation AJAX:", err));
        });
    }

    /* ==========================================================================
       9. SOUMISSION ASYNCHRONE DES AVIS CLIENTS
       ========================================================================== */
    const reviewForm = document.getElementById('async-review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const menuId = document.getElementById('modal_menu_id').value;
            const commandeId = document.getElementById('modal_commande_id').value;
            const note = document.getElementById('review_note').value;
            const commentaire = document.getElementById('review_comment').value;

            fetch('/client-submit-review-async', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    menu_id: menuId,
                    commande_id: commandeId,
                    note: note,
                    commentaire: commentaire
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // 1. Fermer le modal
                    const modalEl = document.getElementById('reviewModal');
                    const modalInst = bootstrap.Modal.getInstance(modalEl);
                    if (modalInst) modalInst.hide();

                    // 2. Transformer le bouton en badge "Avis envoyé !" dans l'accordéon
                    const container = document.getElementById(`review-container-${commandeId}-${menuId}`);
                    if (container) {
                        container.innerHTML = `
                            <span class="badge bg-success rounded-pill px-3 py-2 shadow-sm" style="pointer-events: none; color: var(--bg-cream)!important;">
                                <i class="bi bi-check-circle-fill me-1"></i> Avis envoyé !
                            </span>
                        `;
                    }

                    // 3. Réinitialiser le formulaire
                    reviewForm.reset();

                    // 4. message à côté du titre H1
                    const popReviewMsg = document.getElementById('pop-review-msg');
                    if (popReviewMsg) {
                        popReviewMsg.classList.remove('d-none'); // Affiche la bulle

                        // Sécurité : annule l'ancien minuteur s'il y en a un
                        if (window.reviewMessageTimeout) clearTimeout(window.reviewMessageTimeout);

                        // Fait disparaître la bulle après 4 secondes
                        window.reviewMessageTimeout = setTimeout(() => {
                            popReviewMsg.classList.add('d-none');
                        }, 4000);
                    }

                } else {
                    if (typeof showToast === "function") showToast(data.message, "error");
                }
            })
            .catch(err => console.error("Erreur d'envoi d'avis:", err));
        });
    }

    /* ==========================================================================
       10. MISE À JOUR ASYNCHRONE DU PROFIL
       ========================================================================== */
    const profileForm = document.getElementById('async-profile-form');

    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // 1. Validation Bootstrap native (vérifie que les champs "required" sont remplis)
            if (!profileForm.checkValidity()) {
                e.stopPropagation();
                profileForm.classList.add('was-validated');
                return;
            }

            // 2. Rassemblement des données
            const formData = {
                prenom: document.getElementById('prenom').value,
                nom: document.getElementById('nom').value,
                telephone: document.getElementById('telephone').value,
                adresse: document.getElementById('adresse').value,
                ville: document.getElementById('ville').value,
                code_postal: document.getElementById('code_postal').value,
                pays: document.getElementById('pays').value
            };

            // 3. Envoie au serveur
            fetch('/client-update-profile-async', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Affichage de la bulle de succès à côté du titre H2
                    const popProfileMsg = document.getElementById('pop-profile-msg');
                    if (popProfileMsg) {
                        popProfileMsg.classList.remove('d-none');
                        if (window.profileMessageTimeout) clearTimeout(window.profileMessageTimeout);
                        window.profileMessageTimeout = setTimeout(() => {
                            popProfileMsg.classList.add('d-none');
                        }, 4000);
                    }

                    // Met aussi à jour l'interface si l'utilisateur change son prénom
                    const navbarUserName = document.getElementById('nav-user-firstname');
                if (navbarUserName) navbarUserName.innerText = formData.prenom;

            } else {
                if (typeof showToast === "function") showToast(data.message, "error");
            }
        })
        .catch(err => console.error("Erreur de mise à jour du profil:", err));
    });
}

    /* ==========================================================================
       11. GESTION DES COMMANDES (EMPLOYÉ) - ASYNCHRONE
       ========================================================================== */

    // Fonction centrale pour envoyer la mise à jour
    function updateOrderAsync(orderId, newStatus) {
        // On vérifie si la case "matériel" existe et si elle est cochée
        const materialCheckbox = document.getElementById(`rest_Check_${orderId}`);
        let isMaterialReturned = 0;
        if (materialCheckbox) {
            isMaterialReturned = materialCheckbox.checked ? 1 : 0;
        }

        fetch('/employee-update-order-async', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                commande_id: orderId,
                statut: newStatus,
                restitution_materiel: isMaterialReturned
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // 1. Mettre à jour le texte du bouton
                const dropdownBtn = document.getElementById(`dropdownMenuButton_${orderId}`);
                if (dropdownBtn) dropdownBtn.innerText = newStatus;

                // 2. Mettre à jour la couleur du badge visuel
                const badgeContainer = document.getElementById(`badge-container-${orderId}`);
                if (badgeContainer) {
                    let badgeHtml = '';
                    switch(newStatus) {
                        case 'En attente': badgeHtml = '<span class="badge rounded-pill w-100 py-2" style="background-color: #6c757d !important; color: var(--bg-cream) !important;">En attente</span>'; break;
                        case 'En préparation': badgeHtml = '<span class="badge rounded-pill w-100 py-2" style="background-color: #ff8800 !important; color: var(--bg-cream) !important;">Préparation</span>'; break;
                        case 'En livraison': badgeHtml = '<span class="badge rounded-pill w-100 py-2" style="background-color: #ffc300 !important; color: var(--bg-cream) !important;">En livraison</span>'; break;
                        case 'Livrée': badgeHtml = '<span class="badge rounded-pill w-100 py-2" style="background-color: #65CA00 !important; color: var(--bg-cream) !important;">Livrée</span>'; break;
                        case 'Terminée': badgeHtml = '<span class="badge rounded-pill w-100 py-2" style="background-color: #198754 !important; color: var(--bg-cream) !important;">Terminée</span>'; break;
                        default: badgeHtml = `<span class="badge rounded-pill w-100 py-2" style="background-color: #dc3545 !important; color: var(--bg-cream) !important;">${newStatus}</span>`;
                    }
                    badgeContainer.innerHTML = badgeHtml;
                }

                // 3. Mise à jour visuelle du badge "Matériel"
                const materialBadgeContainer = document.getElementById(`material-badge-container-${orderId}`);
                if (materialBadgeContainer) {
                    if (isMaterialReturned === 1) {
                        materialBadgeContainer.innerHTML = `
                            <span class="badge rounded-pill px-2 py-1" style="background-color: #198754 !important; color: var(--bg-cream) !important; font-size: 0.75rem;">
                                <i class="bi bi-box-seam-fill me-1"></i> Matériel Rendu
                            </span>`;
                    } else {
                        materialBadgeContainer.innerHTML = `
                            <span class="badge vg-box rounded-pill px-2 py-1">
                                <i class="bi bi-exclamation-octagon-fill me-1"></i> À Récupérer
                            </span>`;
                    }
                }

                if (typeof showToast === "function") showToast(data.message, "success");
            } else {
                if (typeof showToast === "function") showToast(data.message, "error");
            }
        })
        .catch(err => console.error("Erreur AJAX employé:", err));
    }
    // ÉCOUTEUR 1 : Clic sur un statut dans le menu déroulant
    document.querySelectorAll('.btn-async-status').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const orderId = this.getAttribute('data-order-id');
            const newStatus = this.getAttribute('data-value');
            updateOrderAsync(orderId, newStatus);
        });
    });

    // ÉCOUTEUR 2 : Clic direct sur la case à cocher du matériel
    document.querySelectorAll('.custom-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const orderId = this.id.replace('rest_Check_', '');
            const dropdownBtn = document.getElementById(`dropdownMenuButton_${orderId}`);
            if (dropdownBtn) {
                const currentStatus = dropdownBtn.innerText.trim();
                // Envoie la mise à jour avec le statut actuel (seul le matériel change)
                updateOrderAsync(orderId, currentStatus);
            }
        });
    });

    /* ==========================================================================
       12. GESTION DES HORAIRES (EMPLOYÉ) - ASYNCHRONE
       ========================================================================== */

    // Fonction utilitaire pour le footer (transforme "12:00" ou "12:00:00" en "12h00")
    function formatTimeForFooter(timeStr) {
        if (!timeStr) return "";
        const parts = timeStr.split(':');
        if (parts.length >= 2) {
            return `${parts[0]}h${parts[1]}`;
        }
        return timeStr;
    }
    document.querySelectorAll('.btn-async-save-schedule').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const horaireId = this.getAttribute('data-horaire-id');

            // 1. Rassemblement de toutes les données de la ligne correspondante
            const payload = {
                horaire_id: horaireId,
                heure_midi_ouverture: document.getElementById(`midi_ouv_${horaireId}`).value,
                heure_midi_fermeture: document.getElementById(`midi_ferm_${horaireId}`).value,
                heure_soir_ouverture: document.getElementById(`soir_ouv_${horaireId}`).value,
                heure_soir_fermeture: document.getElementById(`soir_ferm_${horaireId}`).value,
                est_ouvert: document.getElementById(`input_schedule_${horaireId}`).value
            };

            // 2. Animation de chargement sur le bouton
            const originalIcon = this.innerHTML; // On garde la disquette en mémoire
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            this.disabled = true; // Empêche le multi-clic

            // ÉCOUTEUR : Clic sur "Ouvert" ou "Fermé" dans le dropdown des horaires
    document.querySelectorAll('.schedule-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const horaireId = this.getAttribute('data-horaire-id');
            const value = this.getAttribute('data-value'); // "1" pour Ouvert, "0" pour Fermé
            const label = this.getAttribute('data-label'); // "Ouvert" ou "Fermé"

            // 1. Met à jour le texte du bouton et la valeur de l'input caché
            const dropdownBtn = document.getElementById(`dropdownScheduleButton_${horaireId}`);
            if (dropdownBtn) dropdownBtn.innerText = label;

            const hiddenInput = document.getElementById(`input_schedule_${horaireId}`);
            if (hiddenInput) hiddenInput.value = value;

            // 2. SI FERMÉ : On vide visuellement les heures du Midi et du Soir
            if (value === "0") {
                document.getElementById(`midi_ouv_${horaireId}`).value = "";
                document.getElementById(`midi_ferm_${horaireId}`).value = "";
                document.getElementById(`soir_ouv_${horaireId}`).value = "";
                document.getElementById(`soir_ferm_${horaireId}`).value = "";
            }
        });
    });

            // 3. Envoi au serveur
            fetch('/employee-update-schedule-async', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                // Restauration du bouton disquette
                this.innerHTML = originalIcon;
                this.disabled = false;

               if (data.success) {
                    // 1. Affichage de la bulle à côté du titre H1
                    const popScheduleMsg = document.getElementById('pop-schedule-msg');
                    if (popScheduleMsg) {
                        popScheduleMsg.classList.remove('d-none');

                        // Sécurité pour réinitialiser le timer si l'employé enchaîne les clics
                        if (window.scheduleMessageTimeout) clearTimeout(window.scheduleMessageTimeout);

                        window.scheduleMessageTimeout = setTimeout(() => {
                            popScheduleMsg.classList.add('d-none');
                        }, 4000);
                    }

                    // 2. MISE À JOUR DU FOOTER EN DIRECT
                    const footerSpan = document.getElementById(`footer-hours-${horaireId}`);
                    if (footerSpan) {
                        if (payload.est_ouvert === "0") {
                            // On remet la classe text-danger pour "Fermé"
                            footerSpan.innerHTML = '<span class="text-danger fw-semibold">Fermé</span>';
                        } else {
                            // Vérification des services remplis
                            const hasMidi = payload.heure_midi_ouverture && payload.heure_midi_fermeture;
                            const hasSoir = payload.heure_soir_ouverture && payload.heure_soir_fermeture;

                            const midiStr = hasMidi ? `${formatTimeForFooter(payload.heure_midi_ouverture)} à ${formatTimeForFooter(payload.heure_midi_fermeture)}` : "";
                            const soirStr = hasSoir ? `${formatTimeForFooter(payload.heure_soir_ouverture)} à ${formatTimeForFooter(payload.heure_soir_fermeture)}` : "";

                            // Application de la même logique que tes IF/ELIF Jinja
                            if (hasMidi && hasSoir) {
                                footerSpan.innerHTML = `${midiStr} / ${soirStr}`;
                            } else if (hasMidi) {
                                footerSpan.innerHTML = `Midi : ${midiStr}`;
                            } else if (hasSoir) {
                                footerSpan.innerHTML = `Soir : ${soirStr}`;
                            } else {
                                // Sécurité : si "Ouvert" mais aucune heure remplie
                                footerSpan.innerHTML = '<span class="text-danger fw-semibold">Fermé</span>';
                            }
                        }
                    }
                } else {
                    // En cas d'erreur technique, le toast reste utile pour alerter l'utilisateur
                    if (typeof showToast === "function") showToast(data.message, "error");
                }
            })
            .catch(err => {
                console.error("Erreur AJAX horaires:", err);
                this.innerHTML = originalIcon;
                this.disabled = false;
            });
        });
    });
    /* ==========================================================================
       13. GESTION DE LA CARTE / MENU - ASYNCHRONE
       ========================================================================== */
    document.querySelectorAll('.btn-async-save-menu').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const menuId = this.getAttribute('data-menu-id');

            const payload = {
                menu_id: menuId,
                prix_par_personne: document.getElementById(`prix_menu_${menuId}`).value,
                quantite_restante: document.getElementById(`qty_menu_${menuId}`).value
            };

            // Animation du bouton
            const originalIcon = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            this.disabled = true;

            fetch('/employee-update-menu-async', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                this.innerHTML = originalIcon;
                this.disabled = false;

                if (data.success) {
                    // 1. Mise à jour dynamique du badge de statut du stock
                    const badgeContainer = document.getElementById(`stock-badge-container-${menuId}`);
                    if (badgeContainer) {
                        const qty = parseInt(payload.quantite_restante);
                        let badgeHtml = '';

                        if (qty <= 0) {
                            badgeHtml = '<span class="badge rounded-pill" style="background-color: #dc3545 !important; color: var(--bg-cream) !important;"><i class="bi bi-exclamation-triangle me-1"></i> Rupture</span>';
                        } else if (qty <= 5) {
                            badgeHtml = '<span class="badge rounded-pill" style="background-color: #ffc107 !important; color: var(--bg-cream) !important;"><i class="bi bi-dash-circle me-1"></i> Stock Faible</span>';
                        } else {
                            badgeHtml = '<span class="badge rounded-pill" style="background-color: #198754 !important; color: var(--bg-cream) !important;"><i class="bi bi-check-circle me-1"></i> Disponible</span>';
                        }

                        badgeContainer.innerHTML = badgeHtml;
                    }

                    // 2. Affichage de la bulle à côté du titre
                    const popMenuMsg = document.getElementById('pop-menu-msg');
                    if (popMenuMsg) {
                        popMenuMsg.classList.remove('d-none');

                        // Sécurité pour réinitialiser le timer si l'employé enchaîne les clics
                        if (window.menuMessageTimeout) clearTimeout(window.menuMessageTimeout);

                        window.menuMessageTimeout = setTimeout(() => {
                            popMenuMsg.classList.add('d-none');
                        }, 4000);
                    }
                } else {
                    // En cas d'erreur, on garde le toast pour bien alerter
                    if (typeof showToast === "function") showToast(data.message, "error");
                }
            })
            .catch(err => {
                console.error("Erreur AJAX menu:", err);
                this.innerHTML = originalIcon;
                this.disabled = false;
            });
        });
    });
});