FROM python:3.11-slim

# Instala ttyd e dependências do sistema
RUN apt-get update && apt-get install -y ttyd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do jogo
COPY mesa_de_detetive_animada.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# ttyd usa a porta padrão 7681
EXPOSE 7681

# -W permite digitação no terminal via navegador
CMD ["ttyd", "-p", "7681", "-W", "./entrypoint.sh"]