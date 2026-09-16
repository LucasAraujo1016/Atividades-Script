import re
import sys
from datetime import datetime, time

LOG_FILE = "/var/log/syslog"

# Configuração padrão de data e intervalo de horas
DIA_ALVO = "Sep 15"
HORA_INICIO = 14
HORA_FIM = 15

# Captura o dia (Mon DD) e o horário (HH:MM:SS) no início da linha
TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2})\s(\d{2}:\d{2}:\d{2})")


def filtrar_por_horario(
    caminho_log: str, dia_alvo: str, hora_inicio: int, hora_fim: int
):
    # Filtra as linhas do log correspondentes ao dia e intervalo de horário especificados
    resultados = []
    limite_inicio = time(hour=hora_inicio, minute=0, second=0)
    limite_fim = time(hour=hora_fim, minute=0, second=0)

    # Normaliza espaçamento do dia alvo
    dia_alvo_normalizado = " ".join(dia_alvo.split())

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Extrai a data e a hora da linha
                match = TIMESTAMP_PATTERN.search(linha)
                if not match:
                    continue

                dia_linha = " ".join(match.group(1).split())
                hora_str = match.group(2)

                # Ignora linhas fora do dia selecionado
                if dia_linha != dia_alvo_normalizado:
                    continue

                # Valida se o horário está dentro do intervalo
                hora_evento = datetime.strptime(hora_str, "%H:%M:%S").time()
                if limite_inicio <= hora_evento < limite_fim:
                    resultados.append(linha.rstrip("\n"))
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    return resultados


def main():
    # Lê argumentos de linha de comando ou utiliza os valores padrão
    dia_alvo = sys.argv[1] if len(sys.argv) > 1 else DIA_ALVO
    hora_inicio = int(sys.argv[2]) if len(sys.argv) > 2 else HORA_INICIO
    hora_fim = int(sys.argv[3]) if len(sys.argv) > 3 else HORA_FIM

    eventos = filtrar_por_horario(LOG_FILE, dia_alvo, hora_inicio, hora_fim)

    if not eventos:
        print(
            f"Nenhum evento encontrado em {dia_alvo} entre "
            f"{hora_inicio}h e {hora_fim}h."
        )
        return

    # Exibe as entradas do log filtradas e o total de ocorrências
    print(f"Eventos em {dia_alvo} entre {hora_inicio}h e {hora_fim}h:")
    print("-" * 70)
    for linha in eventos:
        print(linha)

    print(f"\nTotal de eventos na janela: {len(eventos)}")


if __name__ == "__main__":
    main()
