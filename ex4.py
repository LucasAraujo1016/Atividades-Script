Python 3.13.2 (tags/v3.13.2:4f8bb39, Feb  4 2025, 15:23:48) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import re
... from collections import defaultdict
... 
... LOG_FILE = "/var/log/auth.log"
... 
... TIMESTAMP_PATTERN = re.compile(r"^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")
... 
... # Padrões regex para identificar motivos de rejeição e capturar o usuário/IP
... MOTIVOS = [
...     ("Usuário inexistente", re.compile(r"Invalid user (\S+) from")),
...     (
...         "Não permitido (falta de permissão)",
...         re.compile(r"User (\S+) from \S+ not allowed because"),
...     ),
...     (
...         "Falha de autenticação PAM",
...         re.compile(r"pam_unix\(sshd:auth\): authentication failure;.*user=(\S+)"),
...     ),
...     (
...         "Conexão recusada antes da autenticação",
...         re.compile(r"refused connect from (\S+)"),
...     ),
... ]
... 
... 
... def identificar_rejeicoes(caminho_log: str):
...     # Lê o log linha a linha e agrupa as ocorrências pelo motivo correspondente
...     resultados = defaultdict(list)
... 
...     try:
...         with open(caminho_log, "r", encoding="utf-8", errors="ignore") as f:
...             for linha in f:
...                 # Extrai timestamp da linha
...                 ts_match = TIMESTAMP_PATTERN.search(linha)
...                 data_hora = ts_match.group(1) if ts_match else "N/D"
... 
                # Compara a linha com cada padrão cadastrado
                for motivo, padrao in MOTIVOS:
                    match = padrao.search(linha)
                    if match:
                        identificador = match.group(1)
                        resultados[motivo].append((data_hora, identificador))
                        break  # Evita classificar a mesma linha em mais de um motivo
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log não encontrado: {caminho_log}")
        return {}
    except PermissionError:
        print(
            f"[ERRO] Sem permissão para ler {caminho_log}. Execute com sudo."
        )
        return {}

    return resultados


def main():
    # Executa a análise e exibe os resultados formatados na tela
    rejeicoes = identificar_rejeicoes(LOG_FILE)

    if not rejeicoes:
        print("Nenhum login rejeitado por outros motivos foi encontrado.")
        return

    # Imprime os detalhes agrupados por categoria e calcula o total
    total_geral = 0
    for motivo, ocorrencias in rejeicoes.items():
        print(f"\n=== {motivo} ({len(ocorrencias)} ocorrência(s)) ===")
        print(f"{'DATA/HORA':<18} {'USUÁRIO/ORIGEM'}")
        print("-" * 40)
        for data_hora, identificador in ocorrencias:
            print(f"{data_hora:<18} {identificador}")
        total_geral += len(ocorrencias)

    print(f"\nTotal geral de rejeições: {total_geral}")


if __name__ == "__main__":
    main()
