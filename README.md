# 📋 Easy Reminder

Envia lembretes automaticamente para um grupo do Telegram lendo um arquivo de texto simples.

---

## Estrutura do projeto

```
easy_reminder/
├── main.py          # Lê o database.txt e envia os lembretes para o Telegram
├── run_reminder.sh  # Faz git pull e executa o main.py (usado pelo cron)
├── manager.sh       # Gerencia os lembretes via menu interativo
├── database.txt     # Arquivo de lembretes
└── .venv/           # Ambiente virtual Python
```

---

## Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/easy_reminder.git
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
- Adicione o bot ao grupo e acesse `https://api.telegram.org/bot<TOKEN>/getUpdates` para obter o `chat_id`

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

## Gerenciando lembretes (manager.sh)

```bash
chmod +x manager.sh
./manager.sh
```

O menu oferece três opções:

- **Listar** — exibe todos os lembretes cadastrados
- **Inserir** — adiciona um novo lembrete e faz `git push` automaticamente
- **Apagar** — remove um lembrete pelo ID e faz `git push` automaticamente

---

## Automação com cron

```bash
chmod +x run_reminder.sh
```

```cron
25 07 * * * /var/projects/easy_reminder/run_reminder.sh
```

Os logs ficam disponíveis em `/var/log/easy_reminder.log`.
