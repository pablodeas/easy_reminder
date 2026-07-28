#!/usr/bin/env python3

import csv
import os
import subprocess
import sys
import time
import requests

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES  ← edite apenas esta seção
# ─────────────────────────────────────────────
BOT_TOKEN  = "8027753358:AAFDr0xguOatJ__WA-TNi26SYhuL6OkHoo8"
CHAT_ID    = "1070546537"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE   = os.path.join(PROJECT_DIR, "database.txt")
DELAY_MSGS = 1.0  # segundos entre envios
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


def gerar_texto_lembretes(lembretes: list[dict]) -> str:
    """Gera a mensagem calculando a largura máxima de cada coluna para alinhar perfeitamente."""
    if not lembretes:
        return "--- LEMBRETES CADASTRADOS ---\nNenhum lembrete encontrado."

    # Calcula o tamanho do maior texto em cada coluna para fazer o alinhamento
    max_id     = max((len(item.get("ID", "00")) for item in lembretes), default=2)
    max_prazo  = max((len(item.get("PRAZO", "")) for item in lembretes), default=5)
    max_titulo = max((len(item.get("TITULO", "")) for item in lembretes), default=6)

    linhas = ["--- LEMBRETES CADASTRADOS ---"]
    for item in lembretes:
        id_val    = item.get("ID", "00").ljust(max_id)
        prazo     = item.get("PRAZO", "").ljust(max_prazo)
        titulo    = item.get("TITULO", "").ljust(max_titulo)
        descricao = item.get("DESCRICAO", "")

        linhas.append(
            f"ID: {id_val} | Prazo: {prazo} | Título: {titulo} | Descrição: {descricao}".rstrip()
        )

    return "\n".join(linhas)


# ─────────────────────────────────────────────
#  AÇÕES DO SCRIPT
# ─────────────────────────────────────────────

def acao_listar():
    """Exibe a lista de lembretes alinhada no terminal."""
    lembretes = ler_lembretes(DATABASE)
    print(gerar_texto_lembretes(lembretes))


def acao_enviar_telegram():
    """Envia a lista alinhada para o Telegram em bloco de código (fonte monoespaçada)."""
    lembretes = ler_lembretes(DATABASE)
    if not lembretes:
        print("Nenhum lembrete encontrado para enviar ao Telegram.")
        return

    texto_mensagem = gerar_texto_lembretes(lembretes)
    
    # <pre> garante que o Telegram utilize fonte monoespaçada preservando a formatação
    texto_formatado = f"<pre>{texto_mensagem}</pre>"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto_formatado,
        "parse_mode": "HTML"
    }

    print("📤 Enviando lembretes para o Telegram...")
    try:
        resposta = requests.post(url, json=payload, timeout=10)
        resposta.raise_for_status()
        print("✅ Lembretes enviados com sucesso para o Telegram!")
        time.sleep(DELAY_MSGS)
    except requests.exceptions.RequestException as e:
        print(f"❌ [ERRO] Falha ao enviar para o Telegram: {e}")


def acao_inserir():
    """Insere um novo lembrete usando argumentos da mesma linha."""
    if len(sys.argv) < 5:
        print("❌ [ERRO] Parâmetros insuficientes para inserção.")
        print('Uso correto: python3 main.py insert "PRAZO" "TÍTULO" "DESCRIÇÃO"')
        print('Exemplo:     python3 main.py insert "25/05" "Reunião" "Reunião de alinhamento"')
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
  s, send, t, telegram                           Enviar lembretes para o Telegram
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
    elif comando in ["s", "send", "t", "telegram"]:
        acao_enviar_telegram()
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