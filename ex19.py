import re

LOG_FILE = "/var/log/auth.log"
SERVICO_ALVO = "sshd"

TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")

# Padrões para filtrar mensagens geradas pelo serviço e classificar a severidade
SERVICO_PATTERN = re.compile(rf"{SERVICO_ALVO}\[\d+\]:")
NIVEL_PATTERN = re.compile(r"\b(error|warning)\b", re.IGNORECASE)


def buscar_erros_e_avisos(caminho_log: str, servico: str):
    # Percorre o log filtrando mensagens de erro e aviso do serviço especificado
    resultados = []

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                # Ignora linhas que não pertencem ao serviço alvo
                if not SERVICO_PATTERN.search(linha):
                    continue

                # Identifica se a linha contém as palavras 'error' ou 'warning'
                nivel_match = NIVEL_PATTERN.search(linha)
                if not nivel_match:
                    continue

                nivel = nivel_match.group(1).upper()

                # Extrai o timestamp e registra a mensagem
                ts_match = TIMESTAMP_PATTERN.search(linha)
                data_hora = ts_match.group(1) if ts_match else "N/D"

                resultados.append((data_hora, nivel, linha.strip()))
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    return resultados


def main():
    # Executa a busca e exibe o relatório formatado na tela
    ocorrencias = buscar_erros_e_avisos(LOG_FILE, SERVICO_ALVO)

    if not ocorrencias:
        print(f"Nenhum erro ou aviso encontrado para o serviço '{SERVICO_ALVO}'.")
        return

    # Imprime a listagem com data, nível de severidade e conteúdo da mensagem
    print(f"Erros e avisos do serviço '{SERVICO_ALVO}':\n")
    print(f"{'DATA/HORA':<18} {'NÍVEL':<10} {'LINHA'}")
    print("-" * 90)
    for data_hora, nivel, linha in ocorrencias:
        print(f"{data_hora:<18} {nivel:<10} {linha}")

    print(f"\nTotal de ocorrências: {len(ocorrencias)}")


if __name__ == "__main__":
    main()
