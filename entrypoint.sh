#!/bin/bash
# Script de inicialização para aplicação Flask com Gunicorn
# Suporta variáveis de ambiente para configuração

set -e

# Configurações padrão
PORT=${PORT:-5000}
WORKERS=${GUNICORN_WORKERS:-4}
THREADS=${GUNICORN_THREADS:-1}
WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RH Pro - Iniciando Aplicação"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Ambiente: ${FLASK_ENV:-production}"
echo "Porta: $PORT"
echo "Workers: $WORKERS"
echo "Worker Class: $WORKER_CLASS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Executar aplicação com gunicorn
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --threads $THREADS \
    --worker-class $WORKER_CLASS \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    app:app
