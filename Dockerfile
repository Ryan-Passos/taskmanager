# imagem base do Python
FROM python:3.10.4

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos de requisitos para instalar as dependências
COPY requirements.txt requirements.txt

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo do projeto para o diretório de trabalho
COPY . .

# Define a variável de ambiente para o Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Exponha a porta que o Flask usará
EXPOSE 5000

# Comando para iniciar o servidor Flask
CMD ["flask", "run"]
