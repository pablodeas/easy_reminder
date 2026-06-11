# 📋 Easy Reminder

Envia lembretes automaticamente para um grupo do Telegram lendo um arquivo de texto simples.

---

## Como funciona

1. Lê o arquivo `database.txt` linha a linha
2. Monta uma mensagem formatada com todos os lembretes
3. Envia a mensagem para um grupo do Telegram via Bot API

---

## Estrutura do projeto

```
easy_reminder/
├── main.py          # Script principal
├── run_reminder.sh  # Script de automação (git pull + execução)
├── database.txt     # Arquivo de lembretes
└── .venv/           # Ambiente virtual Python
```

---

## Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/pablodeas/easy_reminder
cd easy_reminder
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
python -m venv .venv
source .venv/bin/activate
pip install requests
```

### 3. Configure o bot do Telegram

- Crie um bot via [@BotFather](https://t.me/BotFather) e copie o token
- Adicione o bot ao grupo desejado
- Envie uma mensagem no grupo e acesse `https://api.telegram.org/bot<TOKEN>/getUpdates` para obter o `chat_id` (valor negativo, ex: `-1001234567890`)

### 4. Preencha as credenciais em `main.py`

```python
BOT_TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID   = "SEU_CHAT_ID_AQUI"
```

---

## Formato do database.txt

```
ID;PRAZO;DESCRICAO
01;25/05;Enviar relatorio de analise
02;28/05;Reuniao com equipe de marketing
```

---

## Automação com cron

Copie o script para o servidor e dê permissão de execução:

```bash
chmod +x /var/projects/easy_reminder/run_reminder.sh
```

Adicione ao crontab (`crontab -e`) para rodar todo dia às 07:25:

```cron
25 07 * * * /var/projects/easy_reminder/run_reminder.sh
```

Os logs ficam disponíveis em `/var/log/easy_reminder.log`.