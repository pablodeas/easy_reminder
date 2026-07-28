#!/usr/bin/env python3

import csv
import os
import subprocess
import sys

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES  ← edite apenas esta seção
# ─────────────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(PROJECT_DIR, "database.txt")
# ─────────────────────────────────────────────


def atualizar_repositorio():
    """Executa 'git pull' antes de rodar o script."""
    try:
        subprocess.run(["git", "pull"], cwd=PROJECT_DIR, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ [AVISO] Falha ao executar 'git pull'. Prosseguindo com a base local.")


def enviar_para_git(mensagem_commit: str):
    """Adiciona, commita e envia as alterações via git."""
    print("\n📦 Salvando alteração no repositório...")
    try:
        subprocess.run(["git", "add", DATABASE], cwd=PROJECT_DIR, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", mensagem_commit], cwd=PROJECT_DIR, check=True, capture_output=True)
        subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, capture_output=True, text=True)
        print("✅ Alteração enviada ao repositório com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"❌ [ERRO] Falha no git push:\n{e.stderr}")


def ler_lembretes(caminho: str) -> list[dict]:
    """Lê o arquivo CSV separado por ';' e retorna lista de dicionários."""
    lembretes = []
    try:
        with open(caminho, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for linha in reader:
                lembrete = {k.strip(): v.strip() for k, v in linha.items() if k}
                if any(lembrete.values()):
                    lembretes.append(lembrete)
    except FileNotFoundError:
        return []
    return lembretes


def salvar_lembretes(caminho: str, lembretes: list[dict]):
    """Escreve a lista de lembretes atualizada no arquivo CSV com o cabeçalho correto."""
    fieldnames = ["ID", "PRAZO", "TITULO", "DESCRICAO"]
    with open(caminho, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(lembretes)


def reordenar_ids(caminho: str) -> list[dict]:
    """Reordena sequencialmente os IDs com 2 dígitos (01, 02, 03...) e atualiza o arquivo."""
    lembretes = ler_lembretes(caminho)
    if not lembretes:
        return []

    for index, lembrete in enumerate(lembretes, start=1):
        lembrete["ID"] = f"{index:02d}"

    salvar_lembretes(caminho, lembretes)
    return lembretes


# ─────────────────────────────────────────────
#  AÇÕES DO SCRIPT
# ─────────────────────────────────────────────

def acao_listar():
    """Exibe a lista de lembretes no terminal no formato clássico requested."""
    lembretes = ler_lembretes(DATABASE)
    print("--- LEMBRETES CADASTRADOS ---")
    if not lembretes:
        print("Nenhum lembrete encontrado.")
        return

    for item in lembretes:
        id_val = item.get("ID", "00")
        prazo = item.get("PRAZO", "")
        titulo = item.get("TITULO", "")
        descricao = item.get("DESCRICAO", "")

        if titulo:
            print(f"ID: {id_val} | Prazo: {prazo} | Título: {titulo} | Descrição: {descricao}")
        else:
            print(f"ID: {id_val} | Prazo: {prazo} | Descrição: {descricao}")


def acao_inserir():
    """Insere um novo lembrete usando argumentos da mesma linha."""
    if len(sys.argv) < 5:
        print("❌ [ERRO] Parâmetros insuficientes para inserção.")
        print('Uso correto: python3 main.py insert "PRAZO" "TÍTULO" "DESCRIÇÃO"')
        print('Exemplo:     python3 main.py insert "25/05" "Reunião" "Reunião de alinhamento com equipe"')
        sys.exit(1)

    prazo = sys.argv[2].strip()
    titulo = sys.argv[3].strip()
    descricao = sys.argv[4].strip()

    lembretes = ler_lembretes(DATABASE)
    novo_lembrete = {
        "ID": "00",
        "PRAZO": prazo,
        "TITULO": titulo,
        "DESCRICAO": descricao
    }

    lembretes.append(novo_lembrete)
    salvar_lembretes(DATABASE, lembretes)

    lembretes_atualizados = reordenar_ids(DATABASE)
    novo_id = f"{len(lembretes_atualizados):02d}"
    print(f"✅ Lembrete #{novo_id} inserido com sucesso.")

    enviar_para_git(f"lembrete: adiciona #{novo_id} - {titulo}")


def acao_deletar():
    """Deleta um lembrete usando o ID fornecido na linha de comando."""
    if len(sys.argv) < 3:
        print("❌ [ERRO] Informe o ID do lembrete que deseja excluir.")
        print("Uso correto: python3 main.py delete <ID>")
        print("Exemplo:     python3 main.py delete 05")
        sys.exit(1)

    id_entrada = sys.argv[2].strip()

    try:
        id_alvo = int(id_entrada)
    except ValueError:
        print(f"❌ [ERRO] ID '{id_entrada}' inválido. Digite um número como 05 ou 5.")
        sys.exit(1)

    lembretes = ler_lembretes(DATABASE)
    if not lembretes:
        print("Nenhum lembrete encontrado para deletar.")
        return

    lembretes_filtrados = []
    removido = None

    for item in lembretes:
        try:
            item_id = int(item.get("ID", 0))
        except ValueError:
            item_id = -1

        if item_id == id_alvo:
            removido = item
        else:
            lembretes_filtrados.append(item)

    if not removido:
        print(f"❌ Nenhum lembrete encontrado com o ID {id_entrada}.")
        return

    salvar_lembretes(DATABASE, lembretes_filtrados)
    reordenar_ids(DATABASE)

    id_formatado = f"{id_alvo:02d}"
    print(f"✅ Lembrete #{id_formatado} removido com sucesso.")

    enviar_para_git(f"lembrete: remove #{id_formatado}")


def exibir_ajuda():
    print("""
Uso: python3 main.py <comando> [argumentos]

Comandos disponíveis:
  l, list                                        Listar lembretes cadastrados
  i, insert "PRAZO" "TÍTULO" "DESCRIÇÃO"         Inserir um lembrete em uma única linha
  d, delete <ID>                                 Deletar um lembrete pelo ID (ex: 05)
  h, help                                        Exibir esta mensagem de ajuda
""")


def main():
    atualizar_repositorio()
    reordenar_ids(DATABASE)

    if len(sys.argv) < 2:
        exibir_ajuda()
        sys.exit(1)

    comando = sys.argv[1].lower()

    if comando in ["l", "list"]:
        acao_listar()
    elif comando in ["i", "insert"]:
        acao_inserir()
    elif comando in ["d", "delete"]:
        acao_deletar()
    elif comando in ["h", "help"]:
        exibir_ajuda()
    else:
        print(f"[ERRO] Comando '{comando}' não reconhecido.")
        exibir_ajuda()
        sys.exit(1)


if __name__ == "__main__":
    main()