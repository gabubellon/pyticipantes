# Estágio 1: gera a documentação (MkDocs) que o app serve em /docs/
FROM python:3.13-slim AS docs
WORKDIR /src
COPY pyproject.toml .
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir --group docs
COPY mkdocs.yml .
COPY docs ./docs
COPY hooks ./hooks
COPY src/pyticipantes/exemplos ./src/pyticipantes/exemplos
RUN mkdocs build -q

# Estágio 2: app
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTICIPANTES_HOST=0.0.0.0
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY --from=docs /src/src/pyticipantes/site ./src/pyticipantes/site
RUN pip install --no-cache-dir .
# Dados do usuário: monte volumes em /app/data e /app/saida (veja docker-compose.yml)
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/saude', timeout=3)"
CMD ["pyticipantes"]
