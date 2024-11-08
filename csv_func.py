import csv
from datetime import datetime

def enregistrer_action_csv(utilisateur, employ, livre, action):
    filename = 'historique_actions.csv' if action == "Reserver" else "Historique_rendues.csv"
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        date_heure = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([utilisateur, employ, livre, action, date_heure])

def addcsv(user, empty, livre, action):
    filename = f"livre_{action}.csv"
    with open(filename, mode="a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        date_heure = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([user, empty, livre, date_heure])
