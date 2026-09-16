import re

LOG_FILE = "/var/log/syslog"

TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")
BOOT_PATTERN = re.compile(r"kernel:.*Linux version")


def encontrar_ultimo_boot(caminho_log: str):
    # Percorre o log sequencialmente guardando o último timestamp de inicialização do kernel
    ultimo_boot = None

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Verifica se a linha indica inicialização do kernel
                if BOOT_PATTERN.search(linha):
                    ts_match = TIMESTAMP_PATTERN.search(linha)
                    if ts_match:
                        # Sobrescreve a cada ocorrência para reter apenas a mais recente
                        ultimo_boot = ts_match.group(1)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return None
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return None

    return ultimo_boot


def main():
    # Executa a busca e exibe o resultado do último boot
    ultimo_boot = encontrar_ultimo_boot(LOG_FILE)

    if ultimo_boot:
        print(f"Último boot do sistema registrado em: {ultimo_boot}")
    else:
        print("Nenhum evento de boot encontrado no log.")


if __name__ == "__main__":
    main()
