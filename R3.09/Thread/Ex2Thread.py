import threading
import time

def countdown_thread_1():
    count = 5
    while count > 0:
        print(f"thread 1 : {count}")
        count -= 1
        time.sleep(0.5)

def countdown_thread_2():
    count = 3
    while count > 0:
        print(f"thread 2 : {count}")
        count -= 1
        time.sleep(0.5)

# Création des threads
t1 = threading.Thread(target=countdown_thread_1)
t2 = threading.Thread(target=countdown_thread_2)

t1.start()
t2.start()

t1.join()
t2.join()
