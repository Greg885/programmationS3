import threading
import time

def task(i):
 print(f"Je suis la thread {i+1}")
 time.sleep(1)

T = []
for i in range(2):
 T.append(threading.Thread(target=task, args=[i]))
for i in range(len(T)):
 T[i].start()
for i in range(len(T)):
 T[i].join()