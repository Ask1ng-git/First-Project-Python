import tkinter as tk
from tkinter import messagebox, simpledialog
from mail import send_email
from csv_func import enregistrer_action_csv,addcsv
from db import connecter_a_bd,add_requete
from auth import verifier_identifiants
from obj import Livre,Utilisateur

utilisateurs = []

def charger_utilisateurs():
    query = "SELECT * FROM utilisateurs"
    connexion = connecter_a_bd()
    if connexion:
        cursor = connexion.cursor()
        cursor.execute(query)
        utilisateurs_data = cursor.fetchall()
        connexion.close()
        
        global utilisateurs
        utilisateurs = [
            Utilisateur(nom=data[1], prenom=data[2], email=data[5]) 
            for data in utilisateurs_data
        ]

# Initialisation de la bibliothèque
bibliotheque = []

# Fonction mise à jour pour charger les livres et afficher leur statut de réservation
def charger_livres():
    global bibliotheque
    bibliotheque.clear()
    listbox.delete(0, tk.END)
    
    query = """
    SELECT livres.id, livres.titre, livres.auteur, livres.annee, livres.reserve, utilisateurs.nom, utilisateurs.prenom
    FROM livres
    LEFT JOIN utilisateurs ON livres.id_utilisateur_reservation = utilisateurs.id;
    """
    
    connexion = connecter_a_bd()
    
    if connexion:
        cursor = connexion.cursor()
        cursor.execute(query)
        livres_data = cursor.fetchall()
        connexion.close()

        for livre_data in livres_data:
            id, titre, auteur, annee, reserve, nom, prenom = livre_data
            disponible = not bool(reserve)
            utilisateur_reservation = Utilisateur(nom, prenom) if nom and prenom else None
            livre = Livre(id, titre, auteur, annee, reserve, disponible, utilisateur_reservation)
            bibliotheque.append(livre)

            if disponible:
                listbox.insert(tk.END, livre.afficher_livre())
            else:
                utilisateur_info = livre.utilisateur_reservation.afficher_user() if livre.utilisateur_reservation else "Inconnu"
                listbox.insert(tk.END, f"{livre.afficher_livre()} - {utilisateur_info} (Réservé)")
                listbox.itemconfig(tk.END, {'fg': 'gray'})

# Fonction pour réserver un livre
def reserver_livre(utilisateur):
    index = listbox.curselection()
    if index:
        livre_a_reserver = bibliotheque[index[0]]
        askname = simpledialog.askstring("Qui rend le livre", "Entre nom:")
        askfirstname = simpledialog.askstring("Qui rend le livre", "Entre prenom:")
        
        user = next((u for u in utilisateurs if u.nom == askname and u.prenom == askfirstname), None)
        if user:
            if livre_a_reserver.disponible:
                requete = """
                UPDATE livres 
                SET reserve = 1, id_utilisateur_reservation = (
                    SELECT id FROM utilisateurs WHERE identifiant = %s
                ) 
                WHERE titre = %s AND auteur = %s AND annee = %s
                """
                params = (utilisateur, livre_a_reserver.titre, livre_a_reserver.auteur, livre_a_reserver.annee)
                add_requete(requete, params)

                messagebox.showinfo("Réservation", f"Réservation effectuée pour '{livre_a_reserver.titre}' par {askname}.")
                enregistrer_action_csv(askname, utilisateur, livre_a_reserver.titre, action="Reserver")
                
                # Envoie de l'email
                send_email(user.email,user.nom,"Livres Reserver",livre_a_reserver.titre,user.prenom)
                
                charger_livres()
            else:
                messagebox.showwarning("Erreur", "Ce livre est déjà réservé.")
        else:
            messagebox.showwarning("Erreur", f"L'utilisateur {askname} {askfirstname} n'existe pas")
    else:
        messagebox.showwarning("Erreur", "Veuillez sélectionner un livre à réserver.")


# Fonction pour dereserver un livre
def dereserver_livre(utilisateur):
    index = listbox.curselection()
    if index:
        livre_a_reserver = bibliotheque[index[0]]
        askname = simpledialog.askstring("Qui rend le livre", "Entre nom:")
        askfirstname = simpledialog.askstring("Qui rend le livre", "Entre prenom:")
        
        user = next((u for u in utilisateurs if u.nom == askname and u.prenom == askfirstname), None)
        if user:
            if not livre_a_reserver.disponible:
                requete = """
                UPDATE livres 
                SET reserve = 0, id_utilisateur_reservation = NULL 
                WHERE titre = %s AND auteur = %s AND annee = %s
                """
                params = (livre_a_reserver.titre, livre_a_reserver.auteur, livre_a_reserver.annee)
                add_requete(requete, params)

                messagebox.showinfo("Rendu", f"Le livre '{livre_a_reserver.titre}' a été rendu par {askname}.")
                enregistrer_action_csv(askname,utilisateur,livre_a_reserver.titre,action="Rendu")

                send_email(user.email,user.nom,"Livres Rendu",livre_a_reserver.titre,user.prenom)

                charger_livres()
            else:
                messagebox.showwarning("Erreur", "Ce livre n'est pas réservé.")
        else:
            messagebox.showerror("Erreur", f"L'utilisateur '{askname}'n'éxiste pas ")
    else:
        messagebox.showerror("Erreur", "Veuillez sélectionner un livre à réservé.")


# Fonction pour ajouter un livre
def ajouter_livre(utilisateur):
    titre = simpledialog.askstring("Titre", "Entrez le titre du livre :")
    auteur = simpledialog.askstring("Auteur", "Entrez le nom de l'auteur :")
    annee = simpledialog.askinteger("Année", "Entrez l'année de publication :")
    
    if titre and auteur and annee:
        query = "INSERT INTO livres (titre, auteur, annee, reserve) VALUES (%s, %s, %s, 0)"
        params = (titre, auteur, annee)
        add_requete(query, params)
        messagebox.showinfo("Ajout", f"Le livre '{titre}' a été ajouté avec succès.")
        addcsv(utilisateur, empty=None, livre=titre, action="add")
        charger_livres()
    else:
        messagebox.showwarning("Erreur", "Veuillez remplir tous les champs pour ajouter un livre.")

# Fonction pour modifier un livre
def modifier_livre(utilisateur):
    index = listbox.curselection()
    if index:
        livre_a_modifier = bibliotheque[index[0]]
        if not livre_a_modifier.disponible:
            return messagebox.showerror("Impossible", f"Le livre {livre_a_modifier.titre} est reserver")
        else:
            nouveau_titre = simpledialog.askstring("Modifier Titre", "Entrez le nouveau titre du livre :", initialvalue=livre_a_modifier.titre)
            nouvel_auteur = simpledialog.askstring("Modifier Auteur", "Entrez le nouveau nom de l'auteur :", initialvalue=livre_a_modifier.auteur)
            nouvelle_annee = simpledialog.askstring("Modifier Année", "Entrez la nouvelle année de publication :", initialvalue=livre_a_modifier.annee)

            if nouveau_titre and nouvel_auteur and nouvelle_annee:
                query = """
                UPDATE livres 
                SET titre = %s, auteur = %s, annee = %s 
                WHERE id = %s
                """
                params = (nouveau_titre, nouvel_auteur, nouvelle_annee, livre_a_modifier.id)
                add_requete(query, params)
                messagebox.showinfo("Modification", f"Le livre '{livre_a_modifier.titre}' a été modifié avec succès.")
                addcsv(utilisateur, livre_a_modifier.titre ,nouveau_titre,action="modify")
                charger_livres()
            else:
                messagebox.showwarning("Erreur", "Veuillez remplir tous les champs pour modifier un livre.")
    else:
        messagebox.showwarning("Erreur", "Veuillez sélectionner un livre à modifier.")

# Fonction pour supprimer un livre
def supprimer_livre(utilisateur):
    index = listbox.curselection()
    if index:
        livre_a_supprimer = bibliotheque[index[0]]
        if not livre_a_supprimer.disponible:  
            return messagebox.showerror("Impossible", f"Le livre {livre_a_supprimer.titre} est reserver")  
        else: 
            confirmation = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer le livre '{livre_a_supprimer.titre}' ?")   
            if confirmation:
                query = "DELETE FROM livres WHERE id = %s"
                params = (livre_a_supprimer.id,)
                add_requete(query, params)
                addcsv(utilisateur, empty=None ,livre=livre_a_supprimer.titre, action=None)
                messagebox.showinfo("Suppression", f"Le livre '{livre_a_supprimer.titre}' a été supprimé avec succès.")
                charger_livres()
    else:
        messagebox.showwarning("Erreur", "Veuillez sélectionner un livre à supprimer.")

# Création de l'application principale
fenetre_principale = tk.Tk()
fenetre_principale.withdraw()  # Cache la fenêtre principale au départ

# Interface de connexion
def interface_connexion():
    def connexion():
        username = entry_identifiant.get()
        password = entry_motdepasse.get()
        
        if verifier_identifiants(username, password):
            fenetre_connexion.destroy()
            interface_livres(username)
        else:
            messagebox.showerror("Erreur", "Identifiant ou mot de passe incorrect.")

    fenetre_connexion = tk.Tk()
    fenetre_connexion.title("Connexion à la Bibliothèque")

    label_identifiant = tk.Label(fenetre_connexion, text="Identifiant:")
    label_identifiant.pack(pady=5)
    entry_identifiant = tk.Entry(fenetre_connexion)
    entry_identifiant.pack(pady=5)

    label_motdepasse = tk.Label(fenetre_connexion, text="Mot de passe:")
    label_motdepasse.pack(pady=5)
    entry_motdepasse = tk.Entry(fenetre_connexion, show="*")
    entry_motdepasse.pack(pady=5)

    bouton_connexion = tk.Button(fenetre_connexion, text="Connexion", command=connexion)
    bouton_connexion.pack(pady=10)

    fenetre_connexion.mainloop()

def interface_livres(utilisateur):
    global listbox, entry_recherche

    charger_utilisateurs()

    fenetre_livres = tk.Toplevel()
    fenetre_livres.title("Bibliothèque de Livres")

    label_recherche = tk.Label(fenetre_livres, text="Recherche:")
    label_recherche.pack(pady=5)
    entry_recherche = tk.Entry(fenetre_livres, font=("Arial", 12))
    entry_recherche.pack(pady=5)
    bouton_rechercher = tk.Button(fenetre_livres, text="Rechercher", command=rechercher_livres, font=("Arial", 12), bg="#4286f4", fg="white")
    bouton_rechercher.pack(pady=5)

    listbox = tk.Listbox(fenetre_livres, font=("Arial", 12), selectbackground="#4286f4", selectforeground="white")
    listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    frame_boutons = tk.Frame(fenetre_livres)
    frame_boutons.pack(pady=10)

    bouton_reserver = tk.Button(frame_boutons, text="Réserver", command=lambda: reserver_livre(utilisateur), font=("Arial", 12), bg="#00b894", fg="black")
    bouton_reserver.pack(side=tk.LEFT, padx=5)

    bouton_rendre = tk.Button(frame_boutons, text="Rendre", command=lambda: dereserver_livre(utilisateur), font=("Arial", 12), bg="#00b894", fg="black")
    bouton_rendre.pack(side=tk.LEFT, padx=5)

    bouton_ajouter = tk.Button(frame_boutons, text="Ajouter", command=lambda : ajouter_livre(utilisateur), font=("Arial", 12), bg="#00cec9", fg="black")
    bouton_ajouter.pack(side=tk.LEFT, padx=5)

    bouton_modifier = tk.Button(frame_boutons, text="Modifier", command= lambda : modifier_livre(utilisateur), font=("Arial", 12), bg="#fab1a0", fg="black")
    bouton_modifier.pack(side=tk.LEFT, padx=5)

    bouton_supprimer = tk.Button(frame_boutons, text="Supprimer", command= lambda :supprimer_livre(utilisateur), font=("Arial", 12), bg="#d63031", fg="black")
    bouton_supprimer.pack(side=tk.LEFT, padx=5)

    charger_livres()

# Fonction de recherche
def rechercher_livres():
    recherche = entry_recherche.get().lower()
    listbox.delete(0, tk.END)

    for livre in bibliotheque:
        if recherche in livre.titre.lower() or recherche in livre.auteur.lower():
            if livre.disponible:
                listbox.insert(tk.END, livre.afficher_livre())
            else:
                utilisateur_info = livre.utilisateur_reservation.afficher_user() if livre.utilisateur_reservation else "Inconnu"
                listbox.insert(tk.END, f"{livre.afficher_livre()} - {utilisateur_info} (Réservé)")
                listbox.itemconfig(tk.END, {'fg': 'gray'})


# Lancer l'interface de connexion au démarrage
interface_connexion()

# Lancer la boucle principale de l'application
fenetre_principale.mainloop()