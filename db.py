import mysql.connector
from mysql.connector import Error

# Fonction de connexion à la base de données
def connecter_a_bd():
    hosts = '' # Nom du serveur MySQL
    try:
        connexion = mysql.connector.connect(
            host=hosts, # Nom du serveur MySQL
            database='', #Nom de la base de données
            user='', # Nom d'utilisateur
            password=''  # Mot de passe de l'utilisateur MySQL
        )
        if connexion.is_connected():
            print(f"Connexion réussie à la base de données {hosts} ")
            return connexion
    except Error as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        return None
    return None

# Fonction pour exécuter une requête SQL (ajout,modif,suppresion)
def add_requete(query, params=None):
    connexion = connecter_a_bd()
    if connexion:
        cursor = connexion.cursor()
        try:
            cursor.execute(query, params)
            connexion.commit()
            return cursor
        except Error as e:
            print(f"Erreur SQL : {e}")
        finally:
            cursor.close()
            connexion.close()