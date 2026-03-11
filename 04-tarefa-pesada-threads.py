from threading import Thread
import time

def tarefa_pesada(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

threads = []
inicio = time.time()

print("####### Processamento paralelo usando threads em 1 núcleo #######")

for _ in range(128):
    t = Thread(target=tarefa_pesada, args=(10_000_000,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

fim = time.time()

print("Tempo com threads:", fim - inicio)