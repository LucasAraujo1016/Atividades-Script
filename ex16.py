import re
from collections import Counter

LOG_FILE = "/var/log/syslog"

# Captura o identificador do serviço logo após o hostname e antes do PID ou dois-pontos
SERVICO_PATTERN = re.compile(
    r"^\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2}\s+\S+\s+([\w\-\.]+)(?:\[\d+\])?:"
)


def contar_mensagens_por_servico(caminho_log: str) -> Counter:
    # Percorre o log contabilizando o número de ocorrências por serviço
    contador = Counter()

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Extrai o nome do serviço da linha e incrementa o totalizador
                match = SERVICO_PATTERN.match(linha)
                if match:
                    servico = match.group(1)
                    contador[servico] += 1
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return Counter()
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return Counter()

    return contador


def main():
    # Executa a contagem e exibe o ranking de serviços por volume de logs
    contagem = contar_mensagens_por_servico(LOG_FILE)

    if not contagem:
        print("Nenhuma mensagem de serviço encontrada no log.")
        return

    # Exibe a tabela ordenada decrescente por quantidade de mensagens
    print(f"{'SERVIÇO':<25} {'QTD. DE MENSAGENS':>18}")
    print("-" * 45)
    for servico, qtd in contagem.most_common():
        print(f"{servico:<25} {qtd:>18}")

    # Identifica e destaca o serviço líder em geração de logs
    servico_top, qtd_top = contagem.most_common(1)[0]
    print(f"\nServiço que mais gera logs: {servico_top} ({qtd_top} mensagens)")


if __name__ == "__main__":
    main()
