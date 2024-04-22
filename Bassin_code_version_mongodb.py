# Librairies 
import smtplib # Librairie pour envoyer des e-mails
import time # Librairie pour gérer le temps
# Librairies pour la gestion des dates et heures
from bson import datetime as bson_datetime
from datetime import datetime, timedelta, timezone 
import json # Librairie pour gérer les fichiers JSON
import smbus # Librairie pour la communication I2C 
from w1thermsensor import W1ThermSensor # Librairie pour le capteur de température DS18B20
import paho.mqtt.client as mqtt # Librairie pour la communication MQTT
import RPi.GPIO as GPIO # Librairie pour les GPIO
import os # Librairie pour les fonctions système
# Librairies pour envoyer des e-mails
from email.mime.text import MIMEText # Librairie pour envoyer des e-mails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pymongo.mongo_client import MongoClient # Librairie pour la base de données MongoDB


# Créer une instance du capteur DS18B20
sensor_DS18B20 = W1ThermSensor()

# Créer une instance SMBus
bus = smbus.SMBus(1)

# Adresse I2C du SHT35
SHT35_ADDRESS = 0x44

# Module GPIO: BOARD ou BCM
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Définition des broches GPIO
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Définition des broches en entrées ou en sortie #
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Configuration MQTT
broker_address = "10.224.0.246"
broker_port = 1883
topic = "isen/bassiniot/temp"
topic2 = "isen/bassiniot/hum"
topic3 = "isen/bassiniot/temp_eau"
topic4 = "isen/bassiniot/dist"
topic5 = "isen/bassiniot/data"

# Définition de la fonction de rappel pour la connexion MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connexion établie avec succès au broker MQTT.")
        # Abonnez-vous aux topics ici si nécessaire
        # client.subscribe("topic")

    else:
        print("Échec de la connexion au broker MQTT. Code de retour :", rc)

# Fonction de callback pour le message MQTT
def on_message(client, userdata, message):
    # Vérifiez si le message reçu est "ON"
    if message.payload.decode() == "ON":
        envoyer_fichier_json_par_email("data.json")
        vider_fichier_json("data.json")  # Vider le fichier JSON après l'envoi par e-mail
        print("Le message reçu est 'ON'. L'e-mail sera envoyé.")
    else:
        print("Le message reçu n'est pas 'ON'. L'e-mail ne sera pas envoyé.")

def vider_fichier_json(filename):
    with open(filename, 'w') as json_file:
        json_file.write('')
    print("Le fichier JSON a été vidé.")


# Créer une instance du client MQTT
client = mqtt.Client("Python")
client.connect(broker_address, broker_port)
client.subscribe(topic5)

client.on_message = on_message # Définir la fonction de rappel pour le message MQTT

def envoyer_fichier_json_par_email(filename):
    smtp_server = 'email-smtp.eu-west-3.amazonaws.com' # Serveur Francais
    smtp_port = 587
    smtp_username = 'A modifier'
    smtp_password = 'A modifier'
    expediteur = 'bassin.iot@gmail.com'
    destinataire = 'A modifier' # Mettre les adresses e-mail des destinataires sÃ©parÃ©es par des virgules

    # Création du message multipart
    msg = MIMEMultipart()
    msg['Subject'] = "Fichier JSON"
    msg['From'] = expediteur
    msg['To'] = destinataire

    # Ajout du corps du message
    message_body = "Pièce jointe : fichier JSON"
    msg.attach(MIMEText(message_body, 'plain'))

    # Ajout de la pièce jointe (fichier JSON)
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(expediteur, destinataire, msg.as_string())
        server.quit()
        print("E-mail avec fichier JSON envoyé avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail avec fichier JSON : {e}")

# Fonction pour lire les données du SHT35
def read_sht35():
    bus.write_i2c_block_data(SHT35_ADDRESS, 0x2C, [0x06]) # Envoyer une commande de mesure
    time.sleep(0.5)
    data = bus.read_i2c_block_data(SHT35_ADDRESS, 0x00, 6) # Lire les données
    # Convertir les données
    temp = ((data[0] * 256.0) + data[1]) / 65535.0 * 175.0 - 45.0
    humidity = ((data[3] * 256.0) + data[4]) / 65535.0 * 100.0
    return temp, humidity

# Fonction pour lire les données du HC-SR04
def distance():
    # Envoyer un signal HIGH sur la broche TRIGGER
    GPIO.output(GPIO_TRIGGER, True)
    # Attendre 10 µs puis envoyer un signal LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    # Enregistrer le temps de départ et d'arrivée du signal
    StartTime = time.time()
    StopTime = time.time()
    # Enregistrer le temps de départ
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    # Enregistrer le temps d'arrivée
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    # Calculer le temps écoulé et la distance
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    # Si la distance est supérieure à 400 cm, définir la dist>
    if distance > 400:
        distance = 0

    return distance

from pymongo import MongoClient

def insert_data_to_mongodb(temp, temp_eau, humidity, dist):
    # Remplacez les valeurs de MONGO_URI par votre chaîne de connexion MongoDB Atlas
    MONGO_URI = "mongodb+srv://bassiniot:1wxBO00TPS51B2HH@bassiniot.kcm957t.mongodb.net/?retryWrites=true&w=majority&appName=BassinIoT"

    # Créer un client MongoDB et se connecter à la base de données
    client = MongoClient(MONGO_URI)
    db = client.get_database("data_bassin")

    # Créer une collection et insérer un document avec les données
    collection = db.get_collection("data")

    document = {
        "datetime": rounded_datetime_iso,
        "temp": temp,
        "temp_eau": temp_eau,
        "humidity": humidity,
        "dist": dist
    }
    collection.insert_one(document)
    print("Données insérées dans la base de données MongoDB !")

    # Fermer la connexion à la base de données
    client.close()


# Fonction pour envoyer un e-mail à plusieurs destinataires
def envoyer_email(sujet, corps):
    # Paramètres du serveur SMTP (utilisez vos propres informations)
    smtp_server = 'email-smtp.eu-west-3.amazonaws.com' # Serveur Francais
    smtp_port = 587
    smtp_username = 'A modifier'
    smtp_password = 'A modifier'
    expediteur = 'bassin.iot@gmail.com'
    destinataire = 'A modifier' # Mettre les adresses e-mail des destinataires sÃ©parÃ©es par des virgules

    # Créez le message e-mail
    msg = MIMEText(corps)
    msg['Subject'] = sujet
    msg['From'] = expediteur
    msg['To'] = destinataire  # Liste des destinataires séparés par des virgules
    # Établissez la connexion SMTP et envoyez l'e-mail
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(expediteur, destinataire, msg.as_string())
        server.quit()
        print("E-mail envoyé avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

def verifier_seuils():
    # Seuils
    threshold_temp_eau_sup = 25
    threshold_temp_eau_inf = 10
    threshold_temp_air_sup = 30
    threshold_temp_air_inf = 10
    threshold_hum_air_sup = 90
    threshold_hum_air_inf = 20
    threshold_niveau_eau = 15

    # Vérifiez les seuils
    if (temp_eau > threshold_temp_eau_sup):
        envoyer_email("Alerte - Température du bassin", "La température de l'eau est trop haute. La température est de {:.3f}°C".format(temp_eau))
    if (temp_eau < threshold_temp_eau_inf):
        envoyer_email("Alerte - Température du bassin", "La température de l'eau est trop basse. La température est de {:.3f}°C".format(temp_eau))
    if (temp > threshold_temp_air_sup):
        envoyer_email("Alerte - Température de la pièce", "La température de l'eau est trop haute. La température est de {:.3f}°C".format(temp))
    if (temp < threshold_temp_air_inf):
        envoyer_email("Alerte - Température de la pièce", "La température de l'eau est trop basse. La température est de {:.3f}°C".format(temp))
    if (humidity > threshold_hum_air_sup):
        envoyer_email("Alerte - Humidité de la pièce", "L'humidité de l'eau est trop haute. L'humidité est de {:.3f %".format(humidity))
    if (humidity < threshold_hum_air_inf):
        envoyer_email("Alerte - Humidité de la pièce", "L'humidité de l'eau est trop basse. L'humidité est de {:.3f}%".format(humidity))
    if (dist > threshold_niveau_eau):
        envoyer_email("Alerte - Niveau d'eau du bassin", "Le niveau d'eau est trop bas. La distance est de {:.2f} cm".format(dist))

# Fonction pour mettre à jour le fichier JSON avec de nouvelles données
def update_json_file(temp, temp_eau, humidity, dist):
    # Créer un objet JSON avec les valeurs fournies et la date et l'heure actuelles
    temp_eau = round(temp_eau, 3)
    dist = round(dist, 3)


    data_object = {
        "datetime": rounded_datetime_iso ,
        "temp": temp,
        "temp_eau": temp_eau,
        "humidity": humidity,
        "dist": dist
    }

    if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
        try:
            # Charger les données existantes depuis le fichier JSON
            with open('data.json', 'r') as json_file:
                data_list = json.load(json_file)
        except json.decoder.JSONDecodeError:
            # Si le fichier ne peut pas être décodé (peut-être vide ou corrompu), initialiser data_list avec une liste vide
            data_list = []
    else:
        # Si le fichier n'existe pas ou est vide, initialiser data_list avec une liste vide
        data_list = []

    # Ajouter le nouvel objet JSON à la liste des données existantes
    data_list.append(data_object)

    # Écrire la liste mise à jour dans le fichier JSON
    try:
        with open('data.json', 'w') as json_file:
            json.dump(data_list, json_file, indent=4)
    except Exception as e:
        print("Une erreur s'est produite lors de l'écriture dans le fichier :")
        print(e)

    print("Le fichier data.json a été update")

#    client.on_message = on_message

# Vérifier les autorisations du fichier
filename = 'data.json'
if os.access(filename, os.W_OK):
    print("L'utilisateur a les autorisations d'écriture sur le fichier.")
else:
    print("L'utilisateur n'a pas les autorisations d'écriture sur le fichier.")

client.loop_start()

while True:
    # Obtenir la date et l'heure actuelles au format ISO
    original_datetime = datetime.now()
    rounded_datetime = original_datetime - timedelta(seconds=original_datetime.second, microseconds=original_datetime.microsecond)
    rounded_datetime_iso = rounded_datetime.isoformat()

    temp_eau = sensor_DS18B20.get_temperature() # Lire la température du capteur DS18B20
    [temp, humidity] = read_sht35() # Lire la température et l'humidité du capteur SHT35
    dist = distance() # Lire la distance du capteur HC-SR04

    temp = round(temp, 3)
    humidity = round(temp,3)

    print("Température : {:.3f}°C, Humidité : {:.3f}%, Temp_eau: {:.3f}°C, Distance: {:.2f} cm".format(temp, humidity, temp_eau, dist))
    client.publish(topic, str(round(temp, 3)))
    client.publish(topic2, str(round(humidity, 3)))
    client.publish(topic3, str(round(temp_eau, 3)))
    client.publish(topic4, str(round(dist, 2)))
    verifier_seuils()

    insert_data_to_mongodb(temp, temp_eau, humidity, dist)
    update_json_file(temp, temp_eau, humidity, dist)
    # Attendre une seconde avant la prochaine lecture
    time.sleep(3600)

client.loop_stop()