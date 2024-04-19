# Librairies nécessaires
import time
import json
import smbus
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

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

# Définition des broches en entrées ou en sortie 
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Configuration MQTT
broker_address = "10.224.0.246"
broker_port = 1883
topic = "isen/bassiniot/temp"
topic2 = "isen/bassiniot/hum"
topic3 = "isen/bassiniot/temp_eau"
topic4 = "isen/bassiniot/dist"

# Créer une instance du client MQTT
client = mqtt.Client("Python")
client.connect(broker_address, broker_port)

def read_sht35():
    # Envoyer une commande de mesure
    bus.write_i2c_block_data(SHT35_ADDRESS, 0x2C, [0x06])

    # Attendre un peu pour la mesure
    time.sleep(0.5)

    # Lire les données
    data = bus.read_i2c_block_data(SHT35_ADDRESS, 0x00, 6)

    # Convertir les données
    temp = ((data[0] * 256.0) + data[1]) / 65535.0 * 175.0 - 45.0
    humidity = ((data[3] * 256.0) + data[4]) / 65535.0 * 100.0

    return temp, humidity

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

# Initialiser le compteur de temps
seconds_passed = 0

while True:
    # Lire la température du capteur DS18B20
    temp_eau = sensor_DS18B20.get_temperature()

    # Lire la température et l'humidité du capteur SHT35
    [temp, humidity] = read_sht35()

    dist = distance()

    print(seconds_passed)

    # Incrémenter le compteur de temps
    seconds_passed += 1

    # Si 5 minutes se sont écoulées (300 secondes), publier les valeurs
    if seconds_passed >= 10:
        print("Température : {:.3f}°C, Humidité : {:.3f}%, Temp_eau: {:.3f}°C, Distance: {:.2f} cm".format(temp, humidity, temp_eau, dist))
        client.publish(topic, str(round(temp, 3)))
        client.publish(topic2, str(round(humidity, 3)))
        client.publish(topic3, str(round(temp_eau, 3)))
        client.publish(topic4, str(round(dist, 2)))

        # Réinitialiser le compteur de temps
        seconds_passed = 0

    # Attendre une seconde avant la prochaine lecture
    time.sleep(1)
