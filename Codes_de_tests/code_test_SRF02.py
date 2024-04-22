# Librairies importées
import serial
import signal
import sys
import time

# Définition du port série
SERIAL_PORT = '/dev/ttyS0'  # Port série par défaut sur Raspberry Pi

# Configuration de la vitesse de communication (baudrate)
BAUDRATE = 9600

# Configuration du délai d'attente pour la réception de données (en secondes)
TIMEOUT = 1

# Fonction de gestion de signal pour l'interruption (Ctrl+C)
def signal_handler(sig, frame):
    print("Arrêt du programme")
    # Fermer le port série et quitter le programme proprement
    ser.close()
    sys.exit(0)

# Définir un gestionnaire de signal pour SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

try:
    # Ouverture du port série
    ser = serial.Serial(SERIAL_PORT, BAUDRATE)
    print("Port série ouvert avec succès")

    # Boucle pour recevoir et traiter les données du port série
    while True:
        # Début du temps d'attente
        start_time = time.time()

        # Lecture des données depuis le port série avec un délai d'attente
        while (time.time() - start_time) < TIMEOUT:
            serial_data = ser.readline().decode().strip()
            if serial_data:
                # Affichage des données lues si des données ont été reçues
                print("Données reçues depuis le port série:", serial_data)
                break
        else:
            # Affichage d'un message si aucune donnée n'a été reçue dans le délai spécifié
            print("Aucune donnée reçue depuis le port série dans le délai spécifié")

# Gestion des exceptions
except serial.SerialException as e:
    print("Erreur lors de l'ouverture du port série:", e)

# Gestion de l'interruption (Ctrl+C)
except KeyboardInterrupt:
    # Gestion de l'interruption (Ctrl+C) pour arrêter le programme proprement
    print("Arrêt du programme")
    ser.close()  # Fermeture du port série avant de quitter
    sys.exit(0)
