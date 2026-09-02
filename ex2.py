"""
Exercício 2 - Relatório de logins bem-sucedidos
"""

import re
import sys

LOG_FILE = sys.argv[1] if len(sys.argv) > 1 else "/var/log/auth.log"

# Cada linha de login aceito tem o formato:
# "<mes> <dia> <hora> <host> sshd[<pid>]: Accepted password for <usuario> from <ip> port <porta> ssh2"
# O timestamp (mês, dia, hora) já vem no início da própria linha de log, então não precisa calcular, só extraí-lo com regex.
#
# - "(?P<timestamp>^\w{3}\s+\d+\s\d{2}:\d{2}:\d{2})"captura "Mmm D HH:MM:SS" no início da linha (mês abreviado, dia com 1 ou 2 dígitos, hora)
# - "Accepted (?P<metodo>\S+) for": captura o método de autenticação (password ou publickey)
# - "(?P<user>\S+) from": captura o nome do usuário
PATTERN = re.compile(
    r"^(?P<timestamp>\w{3}\s+\d+\s\d{2}:\d{2}:\d{2}).*"
    r"Accepted (?P<metodo>\S+) for (?P<user>\S+) from"
)


def main():
    resultados = []

    try:
        with open(LOG_FILE, "r", errors="ignore") as f:
            for linha in f:
                match = PATTERN.search(linha)
                if match:
                    # syslog não grava o ano, mantendo o timestamp no formato original "Mês Dia HH:MM:SS" tal como aparece no log
                    resultados.append(
                        (match.group("timestamp"), match.group("user"), match.group("metodo"))
                    )
    except FileNotFoundError:
        print(f"Arquivo de log não encontrado: {LOG_FILE}")
        sys.exit(1)

    if not resultados:
        print("Nenhum login bem-sucedido encontrado no log.")
        return

    print(f"{'Data/Hora':<18} {'Usuário':<15} {'Método'}")
    print("-" * 45)
    # Mantem a ordem em que os eventos aparecem no arquivo (ordem cronológica)
    for timestamp, usuario, metodo in resultados:
        print(f"{timestamp:<18} {usuario:<15} {metodo}")


if __name__ == "__main__":
    main()
