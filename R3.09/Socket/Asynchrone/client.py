import socket
import threading

host = '127.0.0.1'
port = 12345


def receive_messages(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message.lower() in ["bye", "arret"]:
                print("Le serveur a quitté la conversation.")
                break
            print(f"Serveur : {message}")
    except:
        print("Déconnecté du serveur.")
    finally:
        client_socket.close()


def send_messages(client_socket):
    try:
        while True:
            message = input("Vous (Client) : ")
            client_socket.send(message.encode())
            if message.lower() in ["bye", "arret"]:
                break
    except:
        print("Erreur lors de l'envoi du message.")
    finally:
        client_socket.close()


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()


start_client()
