# Interfaz web del comparador de políticas MLOps (feature 002).
# La misma imagen sirve en local (docker compose up) y en Hugging Face Spaces (SDK Docker).
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Dependencias (capa cacheada mientras no cambien pyproject.toml / uv.lock)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --group app --no-install-project

# 2) Paquete y aplicación
COPY src ./src
RUN uv sync --frozen --no-dev --group app
COPY app ./app
COPY config ./config
COPY data/raw ./data/raw
COPY results ./results
COPY .streamlit ./.streamlit

# Hugging Face Spaces ejecuta el contenedor con el usuario 1000
RUN useradd --create-home --uid 1000 user && chown -R user:user /app
USER user
ENV HOME=/home/user \
    MPLCONFIGDIR=/tmp/matplotlib

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/_stcore/health')"

# enableXsrfProtection=false: Hugging Face sirve la app dentro de un iframe y, con la protección
# XSRF activa, la subida de archivos (st.file_uploader) responde 403.
CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=7860", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
