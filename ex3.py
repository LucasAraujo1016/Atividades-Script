"""
Exercício 3 - Auditoria do uso do sudo
"""

import re
import sys

LOG_FILE = sys.argv[1] if len(sys.argv) > 1 else "/var/log/auth.log"

# Uma linha típica de uso do sudo tem o formato:
# "<mes> <dia> <hora> <host> sudo: <usuario> : TTY=... ; PWD=... ;
#  USER=root ; COMMAND=<comando>"
#
# - "(?P<timestamp>^\w{3}\s+\d+\s\d{2}:\d{2}:\d{2})": data/hora no início
# - "sudo:\s+(?P<user>\S+)": nome de quem executou o sudo, logo após "sudo:"
# - "COMMAND=(?P<comando>.+)$": tudo que vem depois de "COMMAND=" até o fim da linha
PATTERN = re.compile(
    r"^(?P<timestamp>\w{3}\s+\d+\s\d{2}:\d{2}:\d{2}).*"
    r"sudo:\s+(?P<user>\S+)\s*:.*COMMAND=(?P<comando>.+)$"
)


def main():
    eventos = []

    try:
        with open(LOG_FILE, "r", errors="ignore") as f:
            for linha in f:
                match = PATTERN.search(linha)
                if match:
                    # Guarda o timestamp, usuário e comando no formato de log de auditoria
                    eventos.append(
                        (match.group("timestamp"), match.group("user"), match.group("comando"))
                    )
    except FileNotFoundError:
        print(f"Arquivo de log não encontrado: {LOG_FILE}")
        sys.exit(1)

    if not eventos:
        print("Nenhum uso de sudo encontrado no log.")
        return

    print(f"{'Data/Hora':<18} {'Usuário':<12} {'Comando'}")
    print("-" * 60)
    for timestamp, usuario, comando in eventos:
        print(f"{timestamp:<18} {usuario:<12} {comando}")


if __name__ == "__main__":
    main()
