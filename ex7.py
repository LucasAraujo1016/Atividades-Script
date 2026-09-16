import re

LOG_FILE = "/var/log/syslog"

TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")

# Padrões regex associados aos tipos de evento de desligamento e reinicialização
EVENTOS = [
    ("Reinicialização", re.compile(r"will reboot now", re.IGNORECASE)),
    ("Reinicialização", re.compile(r"systemd\[1\]:.*[Rr]eboot")),
    ("Desligamento", re.compile(r"System is powering down", re.IGNORECASE)),
    ("Desligamento", re.compile(r"shutting down for system halt", re.IGNORECASE)),
    ("Desligamento", re.compile(r"systemd\[1\]: Reached target .*Shutdown")),
]


def listar_eventos_shutdown(caminho_log: str):
    # Percorre o log buscando mensagens de encerramento do sistema
    eventos_encontrados = []

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Compara a linha com cada padrão de evento cadastrado
                for tipo, padrao in EVENTOS:
                    if padrao.search(linha):
                        # Extrai o timestamp e registra a ocorrência
                        ts_match = TIMESTAMP_PATTERN.search(linha)
                        data_hora = ts_match.group(1) if ts_match else "N/D"
                        eventos_encontrados.append((data_hora, tipo, linha.strip()))
                        break  # Evita duplicidade para a mesma linha
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    return eventos_encontrados


def main():
    # Executa a listagem e formata os dados na tela
    eventos = listar_eventos_shutdown(LOG_FILE)

    if not eventos:
        print("Nenhum evento de shutdown/reboot encontrado.")
        return

    # Exibe a tabela de eventos encontrados e a contagem total
    print(f"{'DATA/HORA':<18} {'TIPO':<18} {'LINHA DE LOG'}")
    print("-" * 90)
    for data_hora, tipo, linha in eventos:
        print(f"{data_hora:<18} {tipo:<18} {linha}")

    print(f"\nTotal de eventos encontrados: {len(eventos)}")


if __name__ == "__main__":
    main()
