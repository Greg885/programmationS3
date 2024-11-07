import threading
import time

# Fonction pour le premier thread
def thread_1():
    for _ in range(5):
        print("Je suis la thread 1")
        time.sleep(0.5)

def thread_2():
    for _ in range(5):
        print("Je suis la thread 2")
        time.sleep(0.5)

t1 = threading.Thread(target=thread_1)
t2 = threading.Thread(target=thread_2)

t1.start()
t2.start()

t1.join()
t2.join()
