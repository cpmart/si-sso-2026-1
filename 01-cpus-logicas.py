import os
import psutil

print("CPUs lógicas:", os.cpu_count())
print("CPUs físicas:", psutil.cpu_count(logical=False))

print("\nUso de CPU por núcleo:")
print(psutil.cpu_percent(percpu=True))