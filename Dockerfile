FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=secret,id=pip_ca \
    if [ -f /run/secrets/pip_ca ]; then export PIP_CERT=/run/secrets/pip_ca; fi \
    && pip install --no-cache-dir -r requirements.txt \
    && groupadd --system crm \
    && useradd --system --gid crm --home-dir /app crm \
    && mkdir /app/staticfiles \
    && chown crm:crm /app/staticfiles

COPY --chown=crm:crm . .
USER crm

EXPOSE 8000
