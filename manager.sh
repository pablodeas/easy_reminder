#!/bin/bash

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES  ← edite apenas esta seção
# ─────────────────────────────────────────────
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATABASE="$PROJECT_DIR/database.txt"
# ─────────────────────────────────────────────

# ── Cores ────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'
# ─────────────────────────────────────────────

# Reseta o terminal para evitar bugs de edição de linha (backspace etc.)
stty sane 2>/dev/null

listar() {
    echo ""
    echo -e "${CYAN}${BOLD}📋 LEMBRETES CADASTRADOS${RESET}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

    # Ignora o cabeçalho
    TOTAL=0
    while IFS=';' read -r id prazo descricao; do
        echo -e "  🔔 ${BOLD}#$id${RESET} | 📅 $prazo | 📝 $descricao"
        ((TOTAL++))
    done < <(tail -n +2 "$DATABASE")

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "  Total: ${BOLD}$TOTAL lembrete(s)${RESET}"
    echo ""
}

apagar() {
    listar

    read -e -r -p "$(echo -e ${YELLOW}Digite o ID do lembrete que deseja apagar:${RESET} )" ID_APAGAR

    # Verifica se o ID existe
    if ! grep -q "^${ID_APAGAR};" "$DATABASE"; then
        echo -e "${RED}[ERRO] ID '$ID_APAGAR' não encontrado.${RESET}"
        return
    fi

    # Exibe o registro encontrado e pede confirmação
    LINHA=$(grep "^${ID_APAGAR};" "$DATABASE")
    echo -e "${YELLOW}Apagar o seguinte registro?${RESET}"
    echo -e "  → $LINHA"
    read -e -r -p "$(echo -e ${YELLOW}Confirmar? \(s/N\):${RESET} )" CONFIRMA

    if [[ "$CONFIRMA" =~ ^[Ss]$ ]]; then
        # Remove a linha do arquivo
        TMPFILE=$(mktemp)
        grep -v "^${ID_APAGAR};" "$DATABASE" > "$TMPFILE" && mv "$TMPFILE" "$DATABASE"
        echo -e "${GREEN}✅ Lembrete #$ID_APAGAR removido com sucesso.${RESET}"

        # ── Git: salvar alteração no repositório ─────────────────────
        echo ""
        echo -e "${CYAN}��� Salvando alteração no repositório...${RESET}"
        cd "$PROJECT_DIR" || { echo -e "${RED}[ERRO] Não foi possível acessar o diretório do projeto.${RESET}"; return; }

        git add "$DATABASE"
        git commit -m "lembrete: remove #$ID_APAGAR"
        GIT_PUSH_OUTPUT=$(git push 2>&1)
        GIT_PUSH_STATUS=$?

        if [ $GIT_PUSH_STATUS -eq 0 ]; then
            echo -e "${GREEN}✅ Alteração enviada ao repositório com sucesso.${RESET}"
        else
            echo -e "${RED}[ERRO] Falha no git push:${RESET}"
            echo "$GIT_PUSH_OUTPUT"
        fi
    else
        echo -e "Operação cancelada."
    fi
    echo ""
}

inserir() {
    echo ""
    echo -e "${CYAN}${BOLD}➕ NOVO LEMBRETE${RESET}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

    # Gera próximo ID automaticamente
    # (usa awk para converter "08", "09" etc. em números decimais,
    #  evitando o bug do bash que trata 08/09 como octal inválido)
    ULTIMO_ID=$(tail -n +2 "$DATABASE" | awk -F';' '$1 != "" {print $1+0}' | sort -n | tail -1)
    PROXIMO_ID=$(printf "%02d" $(( ${ULTIMO_ID:-0} + 1 )))
    echo -e "  ID gerado automaticamente: ${BOLD}#$PROXIMO_ID${RESET}"

    read -e -r -p "  📅 Prazo (ex: 25/05): " PRAZO
    if [[ -z "$PRAZO" ]]; then
        echo -e "${RED}[ERRO] Prazo não pode ser vazio.${RESET}"
        return
    fi

    read -e -r -p "  📝 Descrição: " DESCRICAO
    if [[ -z "$DESCRICAO" ]]; then
        echo -e "${RED}[ERRO] Descrição não pode ser vazia.${RESET}"
        return
    fi

    NOVA_LINHA="${PROXIMO_ID};${PRAZO};${DESCRICAO}"
    echo ""
    echo -e "${YELLOW}Inserir o seguinte lembrete?${RESET}"
    echo -e "  → $NOVA_LINHA"
    read -e -r -p "$(echo -e ${YELLOW}Confirmar? \(s/N\):${RESET} )" CONFIRMA

    if [[ ! "$CONFIRMA" =~ ^[Ss]$ ]]; then
        echo -e "Operação cancelada."
        return
    fi

    echo "$NOVA_LINHA" >> "$DATABASE"
    echo -e "${GREEN}✅ Lembrete #$PROXIMO_ID inserido com sucesso.${RESET}"

    # ── Git: salvar alteração no repositório ─────────────────────────
    echo ""
    echo -e "${CYAN}📦 Salvando alteração no repositório...${RESET}"
    cd "$PROJECT_DIR" || { echo -e "${RED}[ERRO] Não foi possível acessar o diretório do projeto.${RESET}"; return; }

    git add "$DATABASE"
    git commit -m "lembrete: adiciona #$PROXIMO_ID - $DESCRICAO"
    GIT_PUSH_OUTPUT=$(git push 2>&1)
    GIT_PUSH_STATUS=$?

    if [ $GIT_PUSH_STATUS -eq 0 ]; then
        echo -e "${GREEN}✅ Alteração enviada ao repositório com sucesso.${RESET}"
    else
        echo -e "${RED}[ERRO] Falha no git push:${RESET}"
        echo "$GIT_PUSH_OUTPUT"
    fi
    echo ""
}

menu() {
    while true; do
        echo ""
        echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
        echo -e "${BOLD}║        🗓️  EASY REMINDER MANAGER      ║${RESET}"
        echo -e "${BOLD}╠══════════════════════════════════════╣${RESET}"
        echo -e "${BOLD}║  1.${RESET} Listar lembretes                  ${BOLD}║${RESET}"
        echo -e "${BOLD}║  2.${RESET} Inserir lembrete                  ${BOLD}║${RESET}"
        echo -e "${BOLD}║  3.${RESET} Apagar lembrete                   ${BOLD}║${RESET}"
        echo -e "${BOLD}║  0.${RESET} Sair                              ${BOLD}║${RESET}"
        echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
        read -e -r -p "  Escolha uma opção: " OPCAO

        case $OPCAO in
            1) listar ;;
            2) inserir ;;
            3) apagar ;;
            0) echo -e "${GREEN}Até logo!${RESET}"; exit 0 ;;
            *) echo -e "${RED}Opção inválida.${RESET}" ;;
        esac
    done
}

# ── Valida se o database.txt existe ──────────────────────────────────
if [ ! -f "$DATABASE" ]; then
    echo -e "${RED}[ERRO] Arquivo '$DATABASE' não encontrado.${RESET}"
    exit 1
fi

git pull

listar

menu
