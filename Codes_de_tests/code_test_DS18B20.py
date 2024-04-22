# Import des librairies 
from w1thermsensor import W1ThermSensor
import time

# Créer une instance du capteur
sensor = W1ThermSensor()

while True:
  # Lire la température du capteur
  temperature = sensor.get_temperature()
  print("Température : {:.3f}°C".format(temperature))
  time.sleep(1)
