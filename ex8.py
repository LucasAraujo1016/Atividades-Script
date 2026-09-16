import re
from collections import Counter

LOG_FILE = "/var/log/syslog"

TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")

# Captura a ação do systemd (Started/Stopping/Stopped) e o nome da unidade
SERVICO_PATTERN = re.compile(
    r"systemd\[1\]:\s+(Started|Stopping|Stopped)\s+(.+?)\.*\s*$"
)


def listar_alteracoes_servicos(caminho_log: str):
    # Percorre o log buscando registros de início ou parada de serviços
    eventos = []

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Verifica se a linha reporta mudança de estado de serviço
                match = SERVICO_PATTERN.search(linha)
                if match:
                    acao, servico = match.group(1), match.group(2)

                    # Extrai o timestamp e armazena a ocorrência
                    ts_match = TIMESTAMP_PATTERN.search(linha)
                    data_hora = ts_match.group(1) if ts_match else "N/D"

                    eventos.append((data_hora, acao, servico))
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    return eventos


def main():
    # Executa a busca e formata a exibição dos eventos encontrados
    eventos = listar_alteracoes_servicos(LOG_FILE)

    if not eventos:
        print("Nenhuma alteração de status de serviço encontrada.")
        return

    # Exibe a lista detalhada das transições de status
    print(f"{'DATA/HORA':<18} {'AÇÃO':<10} {'SERVIÇO'}")
    print("-" * 70)
    for data_hora, acao, servico in eventos:
        print(f"{data_hora:<18} {acao:<10} {servico}")

    # Agrupa e exibe a contagem de ocorrências por serviço
    contagem = Counter(servico for _, _, servico in eventos)
    print("\nResumo por serviço (quantidade de mudanças de status):")
    for servico, qtd in contagem.most_common():
        print(f"  {servico}: {qtd}")


if __name__ == "__main__":
    main()
