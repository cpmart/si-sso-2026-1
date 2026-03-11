from multiprocessing import Pool, freeze_support
import time
import os

def tarefa_pesada(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

if __name__ == "__main__":
    freeze_support()

    print("CPUs lógicas:", os.cpu_count())
    
    print("########## Processamento paralelo entre núcleos ##########")
    
    inicio = time.time()

    with Pool(128) as p:
        resultados = p.map(tarefa_pesada, [10_000_000] * 8)

    fim = time.time()

    print("Tempo com processos:", fim - inicio)
    print("Quantidade de resultados:", len(resultados))
