import os
import platform
import subprocess
import shutil
import psutil




def executar_comando(comando):
    try:
        resultado = subprocess.check_output(
            comando,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        )
        return resultado.strip()
    except Exception:
        return None


def obter_nome_cpu():
    sistema = platform.system()

    if sistema == "Windows":
        saida = executar_comando("wmic cpu get Name")
        if saida:
            linhas = [linha.strip() for linha in saida.splitlines() if linha.strip()]
            if len(linhas) >= 2:
                return linhas[1]

    elif sistema == "Linux":
        if shutil.which("lscpu"):
            saida = executar_comando("lscpu")
            if saida:
                for linha in saida.splitlines():
                    if "Model name:" in linha:
                        return linha.split(":", 1)[1].strip()

        cpuinfo = "/proc/cpuinfo"
        if os.path.exists(cpuinfo):
            try:
                with open(cpuinfo, "r", encoding="utf-8", errors="ignore") as f:
                    for linha in f:
                        if "model name" in linha:
                            return linha.split(":", 1)[1].strip()
            except Exception:
                pass

    elif sistema == "Darwin":
        saida = executar_comando("sysctl -n machdep.cpu.brand_string")
        if saida:
            return saida

        # Apple Silicon pode não preencher machdep.cpu.brand_string em alguns casos
        saida = executar_comando("sysctl -n hw.model")
        if saida:
            return saida

    return platform.processor() or "Não foi possível identificar"


def obter_info_mac_perf_eff():
    """
    Tenta obter núcleos de performance e eficiência no macOS.
    Funciona melhor em Apple Silicon.
    """
    info = {
        "performance": None,
        "efficiency": None
    }

    if platform.system() != "Darwin":
        return info

    perf = executar_comando("sysctl -n hw.perflevel0.physicalcpu")
    eff = executar_comando("sysctl -n hw.perflevel1.physicalcpu")

    if perf and perf.isdigit():
        info["performance"] = int(perf)

    if eff and eff.isdigit():
        info["efficiency"] = int(eff)

    return info


def obter_info_linux_topologia():
    """
    No Linux, tenta mostrar informações extras.
    Não separa P-core/E-core de forma universal.
    """
    if platform.system() != "Linux":
        return None

    if not shutil.which("lscpu"):
        return None

    saida = executar_comando("lscpu")
    if not saida:
        return None

    dados = {}
    chaves_interesse = [
        "Architecture:",
        "CPU(s):",
        "Thread(s) per core:",
        "Core(s) per socket:",
        "Socket(s):"
    ]

    for linha in saida.splitlines():
        for chave in chaves_interesse:
            if linha.startswith(chave):
                dados[chave[:-1]] = linha.split(":", 1)[1].strip()

    return dados


def obter_info_windows_topologia():
    if platform.system() != "Windows":
        return None

    saida = executar_comando("wmic cpu get NumberOfCores,NumberOfLogicalProcessors /format:list")
    if not saida:
        return None

    dados = {}
    for linha in saida.splitlines():
        if "=" in linha:
            k, v = linha.split("=", 1)
            dados[k.strip()] = v.strip()

    return dados


def mostrar_uso_cpu():
    if psutil is None:
        print("\n[AVISO] psutil não está instalado.")
        print("Para mostrar uso total e por núcleo, instale com:")
        print("pip install psutil")
        return

    print("\nColetando uso da CPU por 1 segundo...")
    uso_total = psutil.cpu_percent(interval=1)
    uso_por_nucleo = psutil.cpu_percent(interval=1, percpu=True)

    print(f"Uso total da CPU: {uso_total}%")
    print("Uso por núcleo:")
    for i, uso in enumerate(uso_por_nucleo):
        print(f"  Núcleo lógico {i}: {uso}%")


def main():
    print("=" * 60)
    print("DIAGNÓSTICO DE CPU")
    print("=" * 60)

    print(f"Sistema operacional: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")
    print(f"Processador: {obter_nome_cpu()}")

    print("\nContagem de CPUs:")
    print(f"  Lógicas (os.cpu_count): {os.cpu_count()}")

    if psutil:
        print(f"  Físicas (psutil): {psutil.cpu_count(logical=False)}")
        print(f"  Lógicas (psutil): {psutil.cpu_count(logical=True)}")
    else:
        print("  Físicas (psutil): instale psutil para ver")
        print("  Lógicas (psutil): instale psutil para ver")

    sistema = platform.system()

    if sistema == "Darwin":
        info_mac = obter_info_mac_perf_eff()
        print("\nTopologia no macOS:")
        if info_mac["performance"] is not None:
            print(f"  Núcleos de performance: {info_mac['performance']}")
        else:
            print("  Núcleos de performance: não identificado")

        if info_mac["efficiency"] is not None:
            print(f"  Núcleos de eficiência: {info_mac['efficiency']}")
        else:
            print("  Núcleos de eficiência: não identificado")

    elif sistema == "Linux":
        info_linux = obter_info_linux_topologia()
        print("\nTopologia no Linux:")
        if info_linux:
            for k, v in info_linux.items():
                print(f"  {k}: {v}")
            print("  P-core / E-core: geralmente não disponível de forma universal")
        else:
            print("  Não foi possível obter detalhes com lscpu")

    elif sistema == "Windows":
        info_win = obter_info_windows_topologia()
        print("\nTopologia no Windows:")
        if info_win:
            print(f"  NumberOfCores: {info_win.get('NumberOfCores', 'não identificado')}")
            print(f"  NumberOfLogicalProcessors: {info_win.get('NumberOfLogicalProcessors', 'não identificado')}")
            print("  P-core / E-core: normalmente não disponível por Python puro")
        else:
            print("  Não foi possível obter detalhes com wmic")

    mostrar_uso_cpu()

    print("\nFim do diagnóstico.")
    print("=" * 60)


if __name__ == "__main__":
    main()