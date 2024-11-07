import threading
import time

# Fonction pour le premier thread
def thread_1():
    for _ in range(5):
        print("Je suis la thread 1")
        time.sleep(0.5)  # Délai de 0,5 seconde entre chaque affichage

# Fonction pour le deuxième thread
def thread_2():
    for _ in range(5):
        print("Je suis la thread 2")
        time.sleep(0.5)  # Délai de 0,5 seconde entre chaque affichage

# Création des threads
t1 = threading.Thread(target=thread_1)
t2 = threading.Thread(target=thread_2)

# Démarrage des threads
t1.start()
t2.start()

# Attente de la fin des threads
t1.join()
t2.join()
