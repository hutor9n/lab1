FROM python:3.12-slim

WORKDIR /app

# Встановлення залежностей окремим шаром для кешування
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання вихідного коду
COPY . .

# Відкриття порту вебсервісу
EXPOSE 8000

# Запуск застосунку
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
