import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def send_email(email,name, subjects, livre, first_name):
    from_email = "" #Entrer son adresse mail
    from_password = "" #Entrer son MDP
    to_email = email


    subject = subjects
    if "Reserver" in subject:
        message = f"Le livre {livre} a était emprunter par {first_name} {name} à {datetime.now().strftime('%H:%M le %d-%m-%Y')} "
    else:
        message = f"Le livre {livre} a était rendu par {first_name} {name} à {datetime.now().strftime('%H:%M le %d-%m-%Y')}"

    msg = MIMEText(message,"html")
    msg['subject'] = subject
    msg['to'] = to_email
    msg["from"] = from_email

    gmail = smtplib.SMTP('smtp.gmail.com', 587) #Possibilité de travailler avec son propre serveur SMTP, ici c'est gmail
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email,from_password)
    gmail.send_message(msg)
