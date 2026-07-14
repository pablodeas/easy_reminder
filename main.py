#!/usr/bin/env python3

import csv
import sys
import time
import requests

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES  ← edite apenas esta seção
# ─────────────────────────────────────────────
BOT_TOKEN  = "8027753358:AAFDr0xguOatJ__WA-TNi26SYhuL6OkHoo8"
CHAT_ID    = "1070546537"
DATABASE   = "database.txt"
DELAY_MSGS = 1.0                        # segundos entre mensagens (evita flood)
# ─────────────────────────────────────────────


def ler_lembretes(caminho: str) -> list[dict]:
    """Lê o arquivo CSV separado por ';' e retorna lista de dicionários."""
    lembretes = []
    try:
        with open(caminho, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for linha in reader:
                lembrete = {k.strip(): v.strip() for k, v in linha.items()}
                if any(lembrete.values()):  # ignora linhas totalmente vazias
                    lembretes.append(lembrete)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{caminho}' não encontrado.")
        sys.exit(1)
    return lembretes


def formatar_mensagem(lembretes: list[dict]) -> str:
    """Monta uma única mensagem com todos os lembretes formatados."""
    linhas = [
        "📋 *LEMBRETES DO DIA*",
        "━━━━━━━━━━━━━━━━━━━━━━",
    ]

    for item in lembretes:
        id_val    = item.get("ID", "?")
        prazo     = item.get("PRAZO", "?")
        descricao = item.get("DESCRICAO", "?")

        linhas.append(
            f"🔔*#{id_val}* 📅`{prazo}` 📝{descricao}"
        )
        linhas.append("---")

    return "\n".join(linhas)


def enviar_mensagem(token: str, chat_id: str, texto: str) -> bool:
    """Envia uma mensagem via Telegram Bot API. Retorna True se bem-sucedido."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown",
    }
    try:
        resposta = requests.post(url, json=payload, timeout=10)
        resposta.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"[ERRO HTTP] {e} — resposta: {resposta.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERRO DE REDE] {e}")
    return False


def main():
    print(f"📂 Lendo lembretes de '{DATABASE}'...")
    lembretes = ler_lembretes(DATABASE)

    if not lembretes:
        print("Nenhum lembrete encontrado no arquivo.")
        sys.exit(0)

    print(f"✅ {len(lembretes)} lembrete(s) encontrado(s).")
    print("📤 Enviando mensagem única para o grupo...")

    texto = formatar_mensagem(lembretes)

    if enviar_mensagem(BOT_TOKEN, CHAT_ID, texto):
        print("✅ Mensagem enviada com sucesso!")
    else:
        print("❌ Falha ao enviar a mensagem.")
        sys.exit(1)


if __name__ == "__main__":
    main()