import re

LOG_FILE = "/var/log/auth.log"

TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")

# Padrões para capturar usuário em falhas SSH e via PAM genérico (su, sudo, login)
SSH_PATTERN = re.compile(
    r"sshd\[\d+\]: Failed password for (?:invalid user )?(\S+) from"
)
PAM_PATTERN = re.compile(
    r"pam_unix\((\w+):auth\): authentication failure;.*?user=(\S+)"
)


def extrair_falhas_com_metodo(caminho_log: str):
    # Percorre o log identificando tentativas de autenticação com falha
    resultados = []

    try:
        with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                ts_match = TIMESTAMP_PATTERN.search(linha)
                data_hora = ts_match.group(1) if ts_match else "N/D"

                # Verifica falhas específicas de SSH
                ssh_match = SSH_PATTERN.search(linha)
                if ssh_match:
                    usuario = ssh_match.group(1)
                    resultados.append((data_hora, usuario, "ssh"))
                    continue

                # Verifica falhas reportadas pelo módulo PAM
                pam_match = PAM_PATTERN.search(linha)
                if pam_match:
                    metodo, usuario = pam_match.group(1), pam_match.group(2)
                    resultados.append((data_hora, usuario, metodo))
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return []
    except PermissionError:
        print(f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo.")
        return []

    return resultados


def main():
    # Executa a extração e exibe os logins falhos com usuário e método
    falhas = extrair_falhas_com_metodo(LOG_FILE)

    if not falhas:
        print("Nenhuma tentativa de login falha encontrada.")
        return

    # Exibe a listagem formatada e a contagem total de falhas
    print(f"{'DATA/HORA':<18} {'USUÁRIO':<15} {'MÉTODO'}")
    print("-" * 45)
    for data_hora, usuario, metodo in falhas:
        print(f"{data_hora:<18} {usuario:<15} {metodo}")

    print(f"\nTotal de falhas de autenticação: {len(falhas)}")


if __name__ == "__main__":
    main()
