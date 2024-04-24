import time
import math
import board
import busio
import adafruit_inmp441
  
# Initialise le bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialise le capteur INMP441
microphone = adafruit_inmp441.INMP441(i2c)
  
# Définit une constante pour la référence de niveau de pression acoustique (en volts)
REFERENCE_VOLTAGE = 0.5  # Cette valeur peut nécessiter un ajustement en fonction de votre configuration
  
# Temps d'intégration (en secondes)
integration_time = 0.1  # Vous pouvez ajuster cette valeur selon vos besoins
  
while True:
    # Lit les données du capteur
    mic_reading = microphone.microphone_reading(integration_time)

    # Calcule la puissance du son en fonction des données du capteur
    sound_power = sum([x * x for x in mic_reading]) / len(mic_reading)

    # Convertit la puissance du son en dB SPL (Sound Pressure Level)
    # La formule exacte dépendra de la sensibilité de votre capteur, de la référence de tension, etc.
    # Vous devrez peut-être ajuster cette formule en fonction de votre configuration spécifique
    db_spl = 20 * math.log10(math.sqrt(sound_power) / REFERENCE_VOLTAGE)
  
    # Affiche le niveau sonore en dB SPL
    print("Niveau sonore : {:.2f} dB SPL".format(db_spl))

    # Attente avant la prochaine lecture
    time.sleep(1)
