FROM python:3.13-alpine AS build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk upgrade && \ 
   apk add curl

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --no-cache-dir


FROM python:3.13-alpine AS base

RUN apk upgrade && \ 
   apk add curl

RUN addgroup -g 1000 apigroup \
    && adduser -u 1000 -G apigroup -D apiuser

EXPOSE 80

USER apiuser

WORKDIR /home/apiuser/fastapi_app

COPY --chown=apiuser:apigroup . .

COPY --from=build --chown=apiuser:apigroup /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD curl --include --request GET http://localhost:80/api/healthz || exit 1

CMD [ "uvicorn", "app.main:app", "--port", "80", "--host", "0.0.0.0", "--workers", "4"]