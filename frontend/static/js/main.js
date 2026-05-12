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
