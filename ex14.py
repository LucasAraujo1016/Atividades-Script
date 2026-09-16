import re
from datetime import datetime

LOG_FILE = "/var/log/syslog"

TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")
BOOT_PATTERN = re.compile(r"kernel:.*Linux version")
SHUTDOWN_PATTERNS = [
    re.compile(r"System is powering down", re.IGNORECASE),
    re.compile(r"shutting down for system halt", re.IGNORECASE),
    re.compile(r"systemd\[1\]: Reached target .*Shutdown"),
]


def _parse_timestamp(ts_str: str) -> datetime:
    # Converte timestamp do syslog assumindo o ano corrente
    ano_atual = datetime.now().year
    return datetime.strptime(f"{ano_atual} {ts_str}", "%Y %b %d %H:%M:%S")


def coletar_eventos(caminho_log: str):
    # Percorre o log coletando os timestamps de boot e desligamento
    boots = []
    desligamentos = []

    with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            ts_match = TIMESTAMP_PATTERN.search(linha)
            if not ts_match:
                continue

            # Registra eventos de inicialização ou encerramento
            if BOOT_PATTERN.search(linha):
                boots.append(_parse_timestamp(ts_match.group(1)))
            elif any(p.search(linha) for p in SHUTDOWN_PATTERNS):
                desligamentos.append(_parse_timestamp(ts_match.group(1)))

    return boots, desligamentos


def calcular_uptime(caminho_log: str):
    # Calcula o tempo de atividade com base no último boot registrado
    try:
        boots, desligamentos = coletar_eventos(caminho_log)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return None
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return None

    if not boots:
        print("Nenhum evento de boot encontrado no log.")
        return None

    ultimo_boot = boots[-1]

    # Busca o primeiro desligamento posterior ao boot mais recente
    proximo_desligamento = next(
        (d for d in desligamentos if d > ultimo_boot), None
    )

    if proximo_desligamento:
        fim = proximo_desligamento
        status = f"desligado em {fim.strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        fim = datetime.now()
        status = "ainda em execução (uptime calculado até o momento atual)"

    duracao = fim - ultimo_boot
    return ultimo_boot, fim, duracao, status


def main():
    # Executa o cálculo de uptime e formata a exibição do tempo decorrido
    resultado = calcular_uptime(LOG_FILE)
    if not resultado:
        return

    ultimo_boot, fim, duracao, status = resultado

    dias = duracao.days
    horas, resto = divmod(duracao.seconds, 3600)
    minutos, _ = divmod(resto, 60)

    print(f"Último boot registrado em: {ultimo_boot.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Sistema {status}")
    print(f"Tempo de atividade (uptime): {dias} dia(s), {horas}h {minutos}min")


if __name__ == "__main__":
    main()
