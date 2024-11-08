import socket

host = '127.0.0.1'
port = 10000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

while True:
    message = input("Vous : ")
    client_socket.send(message.encode())
    if message.lower() in ["bye", "arret"]:
        break

    response = client_socket.recv(1024).decode()
    print(f"Serveur : {response}")

client_socket.close()
