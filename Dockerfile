# Используем легкий образ Python
FROM python:3.9-slim

# Отключаем создание кеш-файлов .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Вывод в консоль без буферизации (чтобы логи видеть сразу)
ENV PYTHONUNBUFFERED 1

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем только список зависимостей (для кэширования Docker)
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Команда запуска (используем uvicorn для запуска FastAPI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]