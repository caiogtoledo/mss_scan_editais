# Use uma imagem base do Python com suporte a Debian Buster
FROM python:3.9-slim-buster

# Instale as dependências do Chromium e do FastAPI
RUN apt-get update && apt-get install -y chromium

# Defina uma variável de ambiente para permitir que o Chromium seja executado sem sandbox
ENV CHROME_BIN=/usr/bin/chromium

# Crie um diretório de trabalho para a aplicação
WORKDIR /app

# Copie o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Instale as dependências da aplicação
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante dos arquivos do projeto para o contêiner
COPY . .

# Copie o arquivo .env para o contêiner
COPY .env .env

# Exponha a porta que a aplicação FastAPI irá usar (por exemplo, a porta 8000)
EXPOSE 8000

# Inicie a aplicação FastAPI quando o contêiner for executado
CMD ["/bin/bash", "-c", "source .env && uvicorn main:app --host 0.0.0.0 --port 8000"]
