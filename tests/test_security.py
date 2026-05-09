import requests

# Inscritption d'un utilisateur avec un mot de passe trop faible ("123")
data = {
    'email': 'hacker@test.com',
    'password': '123',
    'prenom': 'Hack',
    'nom': 'User'
}

try:
    response = requests.post('http://127.0.0.1:5000/register', data=data)

    # Vérification si la page retournée contient l'erreur visuelle ou le message d'erreur
    if "is-invalid" in response.text or "critères de sécurité" in response.text:
        print("SÉCURITÉ OK : Le serveur Python a bloqué le mot de passe faible et renvoyé l'erreur !")
    else:
        print("FAILLE : Le serveur semble avoir accepté le mot de passe ou a renvoyé une mauvaise page.")

except requests.exceptions.ConnectionError:
    print("ERREUR : Le serveur Flask (app.py) n'est pas lancé.")