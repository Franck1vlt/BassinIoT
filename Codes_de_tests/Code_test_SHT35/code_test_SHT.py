import smbus
import time

# Créer une instance SMBus
bus = smbus.SMBus(1)

# Adresse I2C du SHT35
SHT35_ADDRESS = 0x44

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


while True:
 [temp, humidity] = read_sht35()
 print("Température : {:.3f}°C, Humidité : {:.3f}%".format(temp, humidity))
 time.sleep(1)