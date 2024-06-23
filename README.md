# REST API для управления sedo.

## Описание
  - REST API для управления доменами из sedo.com.

## Стек
  - FastAPI, zeep.

## Запуск:
  - Находясь в корне проекта, в папке soap_api
  - Создаём и заполняем .env файл по примеру в .env.example
  - Ставим виртуальное окружение 
      - python -m venv venv
  - Устанавливаем зависимости 
      - pip install -r requirements.txt
  - Переходим в папку src 
      - cd ./src
  - Запускаем приложение 
      - python main.py

## Формат csv файлов:
  При добавлении и изменении доменов: name, price, min_price, fix_price, currency, category
  При получении и удалении доменов: name
## Дополнительно:
- http://127.0.0.1:8000/api/v1/docs/ - Документация и интерфейс sedo_api
