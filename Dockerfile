# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.12
FROM python:3.12

# Встановимо змінну середовища
ENV APP_HOME /main

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Скопіюємо інші файли в робочу директорію контейнера
COPY . .

# Встановимо залежності всередині контейнера
RUN pip install -r requirements.txt

# Запустимо наш застосунок всередині контейнера
CMD ["python", "main.py"]