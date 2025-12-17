# Отель

Веб-сайт для управления услугами отеля, разработанный на Django 4.2

## Начало работы

Эти инструкции помогут вам запустить копию проекта на локальной машине для разработки и тестирования.

### Необходимые условия

Перед началом убедитесь, что у вас установлены:
- Python 3.8+
- pip (менеджер пакетов Python)
- Virtualenv (рекомендуется)

### Установка

Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
```
Установите зависимости:
```bash
pip install -r requirements.txt
```
Примените миграции базы данных:
```bash
python manage.py migrate
```
Запустите сервер разработки:
```bash
python manage.py runserver
```
После этого сайт будет доступен по настроенному адресу
## Автор

* **TohtobinMark** - *Initial work* - [TohtobinMark](https://github.com/TohtobinMark)