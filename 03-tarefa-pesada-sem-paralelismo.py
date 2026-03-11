import time

def tarefa_pesada(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

print("########## Processamento sequencial ##########")

inicio = time.time()

for _ in range(128):
    tarefa_pesada(10_000_000)

fim = time.time()

print("Tempo sequencial:", fim - inicio)