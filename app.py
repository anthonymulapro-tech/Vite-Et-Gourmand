from flask import Flask, render_template

# On importe les fonctions du dossier backend
from backend.user import create_user, login_user

# On configure Flask
app = Flask(
    __name__,
    # Pointe vers les fichiers HTML
    template_folder="frontend/templates",
    # Pointe vers les fichiers CSS/JS
    static_folder="frontend/static"
)
@app.route('/')
def home():
    return "Bienvenue sur Vite & Gourmand !"

# Route pour afficher le formulaire d'inscription
@app.route('/register')
def register_page():
    return render_template('auth/register.html')

# Route pour afficher le formulaire de connexion
@app.route('/login')
def login_page():
    return render_template('auth/login.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)