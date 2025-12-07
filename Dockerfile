# Imagem base leve do Python
FROM python:3.10-slim

# Define diretório de trabalho no container
WORKDIR /app

# Instala dependências do sistema (opcional, mas bom prevenir)
RUN apt-get update && apt-get install -y gcc

# Copia e instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto
COPY . .

# Cria pastas para garantir permissões
RUN mkdir -p data/input data/output data/logs

# Expõe a porta 8000
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]