"""
Exercício 1 - Tentativas de login com senha incorreta
"""

import re
import sys
from collections import Counter

LOG_FILE = sys.argv[1] if len(sys.argv) > 1 else "/var/log/auth.log"

# Cada linha de falha de senha no auth.log tem o formato:
# "Failed password for <usuario> from <ip> port <porta> ssh2"
# ou, para usuário inexistente:
# "Failed password for invalid user <usuario> from <ip> port <porta> ssh2"
#
# - "Failed password for": início da mensagem de falha
# - "(?P<user>\S+)": grupo nomeado "user": captura o nome do suário
# - " from ": precede o IP de origem
PATTERN = re.compile(r"Failed password for (?:invalid user )?(?P<user>\S+) from")


def main():
    contagem = Counter()

    try:
        with open(LOG_FILE, "r", errors="ignore") as f:
            for linha in f:
                match = PATTERN.search(linha)
                if match:
                    usuario = match.group("user")
                    # Counter funciona como o "sort | uniq -c" do shell:
                    # cada usuário encontrado incrementa seu próprio contador
                    contagem[usuario] += 1
    except FileNotFoundError:
        print(f"Arquivo de log não encontrado: {LOG_FILE}")
        sys.exit(1)

    if not contagem:
        print("Nenhuma tentativa de senha incorreta encontrada no log.")
        return

    print(f"{'Usuário':<20} {'Tentativas falhas'}")
    print("-" * 40)
    # most_common() já ordena do usuário com mais tentativas para o com menos
    for usuario, total in contagem.most_common():
        print(f"{usuario:<20} {total}")


if __name__ == "__main__":
    main()
