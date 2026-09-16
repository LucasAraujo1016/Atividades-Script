import re
from datetime import datetime, timedelta

LOG_FILE = "/var/log/dpkg.log"

# Extrai data, hora e nome do pacote nas linhas de instalação concluída
INSTALL_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) status installed (\S+?)(?::\S+)? \S+$"
)


def pacotes_instalados_ultima_semana(caminho_log: str, dias: int = 7):
    # Filtra o log buscando pacotes instalados a partir da data de corte informada
    data_corte = datetime.now() - timedelta(days=dias)
    resultados = []

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Compara a linha com o padrão de confirmação de instalação
                match = INSTALL_PATTERN.match(linha)
                if not match:
                    continue

                # Converte os dados de data/hora e verifica o período
                data_str, hora_str, pacote = match.groups()
                timestamp = datetime.strptime(
                    f"{data_str} {hora_str}", "%Y-%m-%d %H:%M:%S"
                )

                if timestamp >= data_corte:
                    resultados.append((timestamp, pacote))
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    return resultados


def main():
    # Executa a filtragem e exibe os pacotes instalados recentemente
    pacotes = pacotes_instalados_ultima_semana(LOG_FILE)

    if not pacotes:
        print("Nenhum pacote instalado nos últimos 7 dias.")
        return

    # Imprime a lista formatada com a data, hora e nome de cada pacote
    print(f"{'DATA/HORA':<20} {'PACOTE'}")
    print("-" * 50)
    for timestamp, pacote in pacotes:
        print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S'):<20} {pacote}")

    print(f"\nTotal de pacotes instalados na última semana: {len(pacotes)}")


if __name__ == "__main__":
    main()
