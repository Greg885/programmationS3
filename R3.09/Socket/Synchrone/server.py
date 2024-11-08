import socket

host = '127.0.0.1'
port = 10000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print("Serveur de chat en attente de connexion...")

client_socket, client_address = server_socket.accept()
print(f"Connexion avec {client_address}")

while True:
    message = client_socket.recv(1024).decode()
    print(f"Client : {message}")

    if message.lower() == "bye":
        print("Le client a quitté la conversation.")
        break
    elif message.lower() == "arret":
        print("Arrêt du serveur.")
        client_socket.send("arret".encode())
        break
    else:
        response = input("Vous : ")
        client_socket.send(response.encode())

client_socket.close()
server_socket.close()

