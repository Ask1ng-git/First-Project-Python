
class Livre:
    def __init__(self, id, titre, auteur, annee, reserve=False, disponible=True, utilisateur_reservation=None):
        self.id = id
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.reserve = reserve
        self.disponible = disponible
        self.utilisateur_reservation = utilisateur_reservation
    
    def afficher_livre(self):
        return f"{self.titre} - {self.auteur} ({self.annee})"


class Utilisateur:
    def __init__(self, nom, prenom, email = None):
        self.nom = nom
        self.prenom = prenom
        self.email = email

    def afficher_user(self):
        return f"{self.nom}, {self.prenom}"