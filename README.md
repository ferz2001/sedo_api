# REST API для управления sedo.

## Описание
  - REST API для управления доменами из sedo.com.

## Стек
  - FastAPI, zeep.

## Запуск:
- Переходим в папку src 
    - cd ./src
- Создаём и заполняем .env файл по примеру в .env.example
- Ставим виртуальное окружение 
    - python -m venv venv
- Устанавливаем зависимости 
    - pip install -r requirements.txt
- Запускаем приложение 
    - python main.py

## Дополнительно:
- http://127.0.0.1:8000/api/v1/auth/openapi/ - Swagger sedo_api
