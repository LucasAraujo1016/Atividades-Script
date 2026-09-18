import re
from collections import defaultdict, deque
from datetime import datetime

LOG_FILE = "/var/log/auth.log"

TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")

# Captura o nome de usuário nos eventos de abertura e fechamento de sessão PAM
OPEN_PATTERN = re.compile(r"session opened for user (\S+?)(?:\(uid=\d+\))?\s")
CLOSE_PATTERN = re.compile(r"session closed for user (\S+?)(?:\(uid=\d+\))?\s*$")


def _parse_timestamp(ts_str: str) -> datetime:
    # Converte a data do log assumindo o ano atual
    ano_atual = datetime.now().year
    return datetime.strptime(f"{ano_atual} {ts_str}", "%Y %b %d %H:%M:%S")


def calcular_tempo_sessoes(caminho_log: str):
    # Emparelha eventos de login e logout usando filas FIFO por usuário
    aberturas_pendentes = defaultdict(deque)
    sessoes_fechadas = []

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                ts_match = TIMESTAMP_PATTERN.search(linha)
                if not ts_match:
                    continue
                timestamp = _parse_timestamp(ts_match.group(1))

                # Registra abertura de sessão na fila do usuário
                open_match = OPEN_PATTERN.search(linha)
                if open_match:
                    usuario = open_match.group(1)
                    aberturas_pendentes[usuario].append(timestamp)
                    continue

                # Casa o logout com a abertura pendente mais antiga do usuário
                close_match = CLOSE_PATTERN.search(linha)
                if close_match:
                    usuario = close_match.group(1)
                    if aberturas_pendentes[usuario]:
                        abertura = aberturas_pendentes[usuario].popleft()
                        duracao = timestamp - abertura
                        sessoes_fechadas.append(
                            (usuario, abertura, timestamp, duracao)
                        )
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return [], {}
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return [], {}

    # Isola sessões abertas que não registraram encerramento no log
    sessoes_em_aberto = {
        usuario: list(horarios)
        for usuario, horarios in aberturas_pendentes.items()
        if horarios
    }

    return sessoes_fechadas, sessoes_em_aberto


def main():
    # Executa a apuração e exibe as sessões fechadas e em aberto
    sessoes_fechadas, sessoes_em_aberto = calcular_tempo_sessoes(LOG_FILE)

    if not sessoes_fechadas and not sessoes_em_aberto:
        print("Nenhuma sessão de login/logout encontrada no log.")
        return

    # Imprime relatório com data de login, logout e duração total calculada
    if sessoes_fechadas:
        print(f"{'USUÁRIO':<12} {'LOGIN':<20} {'LOGOUT':<20} {'DURAÇÃO'}")
        print("-" * 75)
        for usuario, abertura, fechamento, duracao in sessoes_fechadas:
            horas, resto = divmod(duracao.seconds, 3600)
            minutos, _ = divmod(resto, 60)
            duracao_str = f"{duracao.days}d {horas}h {minutos}min"
            print(
                f"{usuario:<12} "
                f"{abertura.strftime('%Y-%m-%d %H:%M:%S'):<20} "
                f"{fechamento.strftime('%Y-%m-%d %H:%M:%S'):<20} "
                f"{duracao_str}"
            )

    # Exibe avisos de usuários que não possuem registro de logout
    if sessoes_em_aberto:
        print("\nSessões ainda em aberto (sem logout registrado no log):")
        for usuario, horarios in sessoes_em_aberto.items():
            for horario in horarios:
                print(
                    f"  {usuario}: login em "
                    f"{horario.strftime('%Y-%m-%d %H:%M:%S')}"
                )


if __name__ == "__main__":
    main()
