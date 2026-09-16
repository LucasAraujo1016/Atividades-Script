import re

LOG_FILE = "/var/log/dpkg.log"

# Captura data, hora e nome do pacote nas linhas de remoção confirmada
REMOVE_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) status not-installed (\S+?)(?::\S+)? \S+$"
)


def pacotes_removidos(caminho_log: str):
    # Lê o log linha a linha e extrai os pacotes com status de remoção concluída
    resultados = []

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Compara a linha com o padrão de pacote removido
                match = REMOVE_PATTERN.match(linha)
                if match:
                    data_str, hora_str, pacote = match.groups()
                    resultados.append((f"{data_str} {hora_str}", pacote))
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    return resultados


def main():
    # Executa a busca e exibe o relatório de pacotes removidos
    removidos = pacotes_removidos(LOG_FILE)

    if not removidos:
        print("Nenhum pacote removido encontrado no log.")
        return

    # Exibe a lista formatada com a data, hora e nome de cada pacote removido
    print(f"{'DATA/HORA':<20} {'PACOTE'}")
    print("-" * 50)
    for data_hora, pacote in removidos:
        print(f"{data_hora:<20} {pacote}")

    print(f"\nTotal de pacotes removidos: {len(removidos)}")


if __name__ == "__main__":
    main()
