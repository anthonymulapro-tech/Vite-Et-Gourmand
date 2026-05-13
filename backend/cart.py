# Calcul de la remise
def calculer_prix_total(quantite, prix_unitaire, min_convives, seuil_reduction, pourcentage_reduction):
    prix_brut = quantite * prix_unitaire
    remise = 0

    # Logique de remise : si la quantité dépasse le (minimum + seuil)
    if quantite >= (min_convives + seuil_reduction):
        remise = prix_brut * (pourcentage_reduction / 100)

    prix_final = prix_brut - remise

    # Renvoie un dictionnaire avec tous les détails
    return {
        "prix_brut": round(prix_brut, 2),
        "remise": round(remise, 2),
        "prix_final": round(prix_final, 2)
    }