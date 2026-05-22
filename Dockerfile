# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências em uma virtual env
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar apenas dependências de runtime (ldap3 pode precisar de libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copiar virtual env do builder
COPY --from=builder /opt/venv /opt/venv

# Copiar aplicação
COPY . .

# Tornar o script de entrada executável
RUN chmod +x entrypoint.sh

# Definir variáveis de ambiente
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production

# Usuário não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 5000

# Comando padrão: usar entrypoint.sh para suportar variável PORT
ENTRYPOINT ["./entrypoint.sh"]
