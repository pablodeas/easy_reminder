#!/bin/bash

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES  ← edite apenas esta seção
# ─────────────────────────────────────────────
PROJECT_DIR="/var/repos/easy_reminder"
PYTHON="$PROJECT_DIR/.venv/bin/python"
MAIN="$PROJECT_DIR/main.py"
LOG="$PROJECT_DIR/easy_reminder.log" 
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# ─────────────────────────────────────────────

log() {
    echo "[$(date '+%d/%m/%Y %H:%M:%S')] $1" >> "$LOG"
}

log "===== INICIANDO EASY REMINDER ====="

# 1. Entrar no diretório do projeto
cd "$PROJECT_DIR" || {
    log "[ERRO] Diretório '$PROJECT_DIR' não encontrado. Abortando."
    exit 1
}

# 2. Atualizar o repositório
log "Executando git pull..."

GIT_OUTPUT=$(GIT_SSH_COMMAND="ssh -i /home/ubuntu/.ssh/prod_repo -o IdentitiesOnly=yes" git pull 2>&1)
GIT_STATUS=$?

log "$GIT_OUTPUT"

if [ $GIT_STATUS -ne 0 ]; then
    log "[ERRO] git pull falhou. Abortando envio dos lembretes."
    exit 1
fi

# 3. Executar o script de lembretes
log "Executando main.py..."
PYTHON_OUTPUT=$("$PYTHON" "$MAIN" 2>&1)
PYTHON_STATUS=$?

log "$PYTHON_OUTPUT"

if [ $PYTHON_STATUS -ne 0 ]; then
    log "[ERRO] main.py encerrou com falha (código $PYTHON_STATUS)."
    exit 1
fi

log "Lembretes enviados com sucesso."
log "===== FIM ====="
