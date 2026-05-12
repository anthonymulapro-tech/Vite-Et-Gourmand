# Calcul de prix avec remise
def calculer_prix_total(quantite, prix_unitaire, min_convives, seuil_reduction, pourcentage_reduction):
    total = quantite * prix_unitaire
    # Logique de remise : si la quantité dépasse le (minimum + seuil)
    if quantite >= (min_convives + seuil_reduction):
        remise = total * (pourcentage_reduction / 100)
        total = total - remise

    return round(total, 2)