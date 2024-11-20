import socket
import threading

host = '127.0.0.1'
port = 12345

# Création du socket serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()
print("Serveur en attente de connexion...")


# Fonction pour gérer la réception des messages d'un client
def handle_receive(client_socket, client_address):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message.lower() in ["bye", "arret"]:
                print(f"{client_address} a quitté la conversation.")
                break
            print(f"Client {client_address} : {message}")
    except:
        print(f"Connexion perdue avec {client_address}")
    finally:
        client_socket.close()


# Fonction pour gérer l'envoi des messages au client
def handle_send(client_socket):
    try:
        while True:
            response = input("Vous (Serveur) : ")
            client_socket.send(response.encode())
            if response.lower() in ["bye", "arret"]:
                break
    except:
        print("Erreur lors de l'envoi du message.")
    finally:
        client_socket.close()


# Boucle principale pour accepter les connexions clients
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connexion établie avec {client_address}")

    # Création des threads pour la réception et l'envoi
    receive_thread = threading.Thread(target=handle_receive, args=(client_socket, client_address))
    send_thread = threading.Thread(target=handle_send, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()

    print(f"Connexion terminée avec {client_address}")

server_socket.close()
