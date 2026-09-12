FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN curl -sLo /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 \
    && chmod +x /usr/local/bin/ttyd

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mesa_de_detetive_animada.py .

EXPOSE 7681

# Executa direto o python3 em um terminal interativo com ttyd
CMD ["ttyd", "-p", "7681", "-W", "python3", "mesa_de_detetive_animada.py"]
