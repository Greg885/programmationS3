import socket
import threading

host = '127.0.0.1'
port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

def receive_messages():
    try :
        while True:
            message = client_socket.recv(1024).decode()
            if message.lower() in ["bye", "arret"]:
                print("Serveur a quitté la conversation.")
                break
            print(f"Serveur : {message}")
    except:
        print("Erreur de socket")
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

while True:
    message = input("Vous : ")
    client_socket.send(message.encode())
    if message.lower() in ["bye", "arret"]:
        break

client_socket.close()

