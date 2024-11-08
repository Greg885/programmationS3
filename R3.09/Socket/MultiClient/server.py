import socket
import threading

host = '127.0.0.1'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()
print("Serveur de discussion en attente de connexions...")

clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            client.send(message)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            client_socket.close()
            break

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Nouvelle connexion de {client_address}")
    clients.append(client_socket)
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
