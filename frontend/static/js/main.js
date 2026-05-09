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
});