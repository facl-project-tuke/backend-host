FROM python:3.10-slim

# Обновление и установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl gnupg2 apt-transport-https \
    unixodbc-dev gcc g++ libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Удаляем конфликтующие ODBC пакеты (если присутствуют)
RUN apt-get update && apt-get remove -y libodbc2 libodbcinst2 unixodbc-common || true

# Добавление ключа и репозитория Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов
COPY . .

# Открытие порта и запуск приложения
EXPOSE 5000
CMD ["python", "app.py"]
