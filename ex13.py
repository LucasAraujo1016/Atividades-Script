import re

LOG_FILE = "/var/log/apt/history.log"

DATE_PATTERN = re.compile(r"^Start-Date:\s*(.+)$", re.MULTILINE)
CMD_PATTERN = re.compile(r"^Commandline:\s*(.+)$", re.MULTILINE)
USER_PATTERN = re.compile(r"^Requested-By:\s*(\S+)", re.MULTILINE)

# Padrões para identificar o tipo principal de ação executada
ACAO_PATTERNS = [
    ("Instalação", re.compile(r"^Install:\s*(.+)$", re.MULTILINE)),
    ("Remoção", re.compile(r"^Remove:\s*(.+)$", re.MULTILINE)),
    ("Remoção completa (purge)", re.compile(r"^Purge:\s*(.+)$", re.MULTILINE)),
    ("Atualização", re.compile(r"^Upgrade:\s*(.+)$", re.MULTILINE)),
]


def rastrear_uso_apt(caminho_log: str):
    # Lê o log e divide o conteúdo em blocos separados por linhas em branco
    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            conteudo = f.read()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    blocos = re.split(r"\n\s*\n", conteudo.strip())
    registros = []

    # Extrai data, usuário, comando e ação de cada bloco de execução
    for bloco in blocos:
        data_match = DATE_PATTERN.search(bloco)
        cmd_match = CMD_PATTERN.search(bloco)
        user_match = USER_PATTERN.search(bloco)

        if not data_match:
            continue

        data_hora = data_match.group(1).strip()
        comando = cmd_match.group(1).strip() if cmd_match else "N/D"
        usuario = user_match.group(1).strip() if user_match else "N/D (root/serviço)"

        # Determina o tipo de operação com base nas diretivas do bloco
        acao = "N/D"
        for nome_acao, padrao in ACAO_PATTERNS:
            if padrao.search(bloco):
                acao = nome_acao
                break

        registros.append((data_hora, usuario, acao, comando))

    return registros


def main():
    # Executa a extração e exibe os registros formatados na tela
    registros = rastrear_uso_apt(LOG_FILE)

    if not registros:
        print("Nenhum registro de uso de apt/apt-get/dpkg encontrado.")
        return

    # Imprime a listagem de comandos executados com autor e ação realizada
    print(f"{'DATA/HORA':<20} {'USUÁRIO':<12} {'AÇÃO':<26} {'COMANDO'}")
    print("-" * 100)
    for data_hora, usuario, acao, comando in registros:
        print(f"{data_hora:<20} {usuario:<12} {acao:<26} {comando}")

    print(f"\nTotal de execuções registradas: {len(registros)}")


if __name__ == "__main__":
    main()
