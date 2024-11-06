import time
import threading

def task(i):
    for i in range(5):
        print(f"Je suis la thread {i}")
        time.sleep(1)

if __name__ == '__main__':

        t1 = threading.Thread(target=task, args=[1])
        t1.start()

        t2 = threading.Thread(target=task, args=[2])
        t2.start()

        t1.join()
        t2.join()