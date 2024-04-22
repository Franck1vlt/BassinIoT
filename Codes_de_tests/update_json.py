# Librairies
import os
import json

# Vérifier les données à écrire
temp = 25.0
temp_eau = 20.0
humidity = 50.0
dist = 30.0

# Vérifier si les données sont correctes
if temp is not None and temp_eau is not None and humidity is not None and dist is not None:
    print("Les données à écrire sont correctes.")
else:
    print("Les données à écrire sont incorrectes. Assurez-vous qu'elles ont des valeurs valides.")

# Vérifier les appels de fonction
# Supposons que la fonction update_json_file soit définie ici

# Fonction pour mettre à jour le fichier JSON avec de nouvelles données
def update_json_file(temp, temp_eau, humidity, dist):
    # Créer un objet JSON avec les valeurs fournies et la date et l'heure actuelles
    temp_eau = round(temp_eau, 3)
    dist = round(dist, 3)


    data_object = {
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


# Appeler la fonction pour mettre à jour le fichier JSON
# Supposons que les variables temp, temp_eau, humidity et dist soient correctement définies
update_json_file(temp, temp_eau, humidity, dist)

# Vérifier les autorisations du fichier
filename = 'data.json'
if os.access(filename, os.W_OK):
    print("L'utilisateur a les autorisations d'écriture sur le fichier.")
else:
    print("L'utilisateur n'a pas les autorisations d'écriture sur le fichier.")

# Lire le contenu du fichier JSON
with open(filename, 'r') as file:
    data = file.read()

if data.strip() == '':
    print("Le fichier data.json est vide.")
else:
    print("Le fichier data.json contient des données :", data)
