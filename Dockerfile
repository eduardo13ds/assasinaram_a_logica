FROM python:3.11-slim

# Instala curl para baixar o binário do ttyd
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Baixa a versão estável mais recente do ttyd direto do GitHub
RUN curl -sLo /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 \
    && chmod +x /usr/local/bin/ttyd

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação
COPY mesa_de_detetive_animada.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Porta padrão de escuta
EXPOSE 7681

# Inicia o ttyd com permissão de escrita (-W)
CMD ["ttyd", "-p", "7681", "-W", "./entrypoint.sh"]
