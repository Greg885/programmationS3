import socket
import threading

host = '127.0.0.1'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print("Serveur en attente de connexion...")

client_socket, client_address = server_socket.accept()
print(f"Connexion avec {client_address}")

def receive_messages():
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message.lower() in ["bye", "arret"]:
                print("Le client a quitté la conversation.")
                break
            print(f"Client : {message}")
    except:
        print("Erreur de socket")

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

try :
    while True:
        response = input("Vous : ")
        client_socket.send(response.encode())
        if response.lower() in ["bye", "arret"]:
            break
except ConnectionResetError or ConnectionError :
    print ("fin de connexion relancer le Serveur")

client_socket.close()
server_socket.close()
