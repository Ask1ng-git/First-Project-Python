from db import connecter_a_bd

# Fonction pour vérifier l'authentification de l'utilisateur
def verifier_identifiants(username, password):
    connexion = connecter_a_bd()
    if connexion:
        cursor = connexion.cursor()
        query = "SELECT * FROM utilisateurs WHERE identifiant = %s AND motdepasse = %s"
        cursor.execute(query, (username, password))
        utilisateur = cursor.fetchone()
        connexion.close()
        return utilisateur is not None
    return False