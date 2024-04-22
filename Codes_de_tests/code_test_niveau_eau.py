# Import des librairies GPIO et time (temps et conversion) #
import RPi.GPIO as GPIO
import time

# Module GPIO: BOARD ou BCM (numérotation comme la sérigraphie de la carte ou co                                                                                                             mme le chip) #
GPIO.setmode(GPIO.BCM)

# Définition des broches GPIO #
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Définition des broches en entrées ou en sortie #
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

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

    # Si la distance est supérieure à 400 cm, définir la distance à 0 cm
    if distance > 400:
        distance = 0

    return distance

# Programme principal 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Distance mesurée = %.1f cm" % dist)
            time.sleep(1)
        # On reset le programme via CTRL+C #
    except KeyboardInterrupt:
        print("Mesure stoppée")
        GPIO.cleanup()
