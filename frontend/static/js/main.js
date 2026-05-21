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
    const subtotalElement = document.getElementById('display_subtotal');

    if (subtotalElement) {
        const discountElement = document.getElementById('display_discount');
        const baseSubtotal = parseFloat(subtotalElement.textContent) || 0;
        const baseDiscount = discountElement ? parseFloat(discountElement.textContent) : 0;

        const deliveryZone = document.getElementById('delivery_zone');
        const distanceContainer = document.getElementById('distance_container');
        const distanceKm = document.getElementById('distance_km');
        const displayDelivery = document.getElementById('display_delivery');
        const displayGrandTotal = document.getElementById('display_grand_total');

        function calculateTotal() {
            let deliveryCost = 0;
            let finalTotal = baseSubtotal - baseDiscount;

            if (deliveryZone.value === 'outside') {
                distanceContainer.classList.remove('d-none');
                let km = parseFloat(distanceKm.value) || 0;
                deliveryCost = km > 0 ? 5 + (km * 0.59) : 5;
            } else {
                distanceContainer.classList.add('d-none');
                distanceKm.value = 0;
            }

            displayDelivery.textContent = deliveryCost.toFixed(2);
            finalTotal += deliveryCost;
            displayGrandTotal.textContent = finalTotal.toFixed(2);
        }

        const btnDistMinus = document.getElementById('btn_dist_minus');
        const btnDistPlus = document.getElementById('btn_dist_plus');

        if (btnDistMinus && btnDistPlus) {
            btnDistMinus.addEventListener('click', function() {
                let currentVal = parseInt(distanceKm.value) || 0;
                if (currentVal > 0) {
                    distanceKm.value = currentVal - 1;
                    calculateTotal();
                }
            });

            btnDistPlus.addEventListener('click', function() {
                distanceKm.value = (parseInt(distanceKm.value) || 0) + 1;
                calculateTotal();
            });
        }

        deliveryZone.addEventListener('change', calculateTotal);
        distanceKm.addEventListener('input', calculateTotal);

        // Menu déroulant custom (Zone de livraison)
        const dropdownZoneItems = document.querySelectorAll('.custom-delivery-dropdown .dropdown-item');
        const selectedZoneText = document.getElementById('selected-zone-text');

        dropdownZoneItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                selectedZoneText.textContent = this.textContent;
                deliveryZone.value = this.getAttribute('data-value');
                deliveryZone.dispatchEvent(new Event('change'));
            });
        });

        calculateTotal();
    }

    // Menu déroulant custom (Heure de livraison)
    const timeItems = document.querySelectorAll('.time-item');
    const selectedTimeText = document.getElementById('selected-time-text');
    const inputHeureLivraison = document.getElementById('heure_livraison');

    if (timeItems.length > 0 && selectedTimeText && inputHeureLivraison) {
        timeItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                selectedTimeText.textContent = this.textContent;
                inputHeureLivraison.value = this.getAttribute('data-value');
            });
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

});