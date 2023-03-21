# Foodgram - Продуктовый помощник


## Стек технологий

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

## Описание проекта

Foodgram - приложение для публикации рецептов различных блюд. Реализован следующий функционал: система аутентификации, просмотр рецептов, создание новых рецептов, их изменение, добавление рецептов в избранное и список покупок, выгрузка списка покупок в pdf-файл, возможность подписки на авторов рецептов. В backend-части проекта использованы следующие инструменты: Python3, Django, DjangoREST Framework, PostgreSQL Также применены: CI/CD - GitHub Actions, Docker, Nginx, YandexCloud

## Установка проекта локально

* Склонировать репозиторий на локальную машину:
```bash
git clone https://github.com/Mane26/foodgram-project-react.git
cd foodgram-project-react
```

* Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

```bash
. venv/bin/activate
```

* Cоздайте файл `.env` в директории `/infra/` с содержанием:

```
SECRET_KEY=секретный ключ django
ALLOWED_HOSTS='ip localhost'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

* Перейти в директирию и установить зависимости из файла requirements.txt:

```bash
cd backend/
pip install -r requirements.txt
```

* Выполните миграции:

```bash
python manage.py migrate
```

* Запустите сервер:
```bash
python manage.py runserver
```

## Запуск проекта в Docker контейнере
* Установите Docker.

Параметры запуска описаны в файлах `docker-compose.yml` и `nginx.conf` которые находятся в директории `infra/`.  
При необходимости добавьте/измените адреса проекта в файле `nginx.conf`

* Запустите docker compose:
```bash
docker-compose up -d --build
```  
  > После сборки появляются 3 контейнера:
  > 1. контейнер базы данных **db**
  > 2. контейнер приложения **backend**
  > 3. контейнер web-сервера **nginx**
* Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```
* Загрузите ингредиенты:
```bash
docker-compose exec backend python manage.py load_ingrs
```
* Загрузите теги:
```bash
docker-compose exec backend python manage.py load_tags
```
* Создайте администратора:
```bash
docker-compose exec backend python manage.py createsuperuser
```
* Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

## Сайт
После запуска проект будут доступен по адресу:
[http://localhost/]

### Workflow
- **tests:** Проверка кода на соответствие PEP8.
- **push Docker image to Docker Hub:** Сборка и публикация образа на DockerHub.
- **deploy:** Автоматический деплой на боевой сервер при пуше в главную ветку main.
- **send_massage:** Отправка уведомления в телеграм-чат.

### Подготовка и запуск проекта на сервере

- Клонировать проект с помощью git clone или скачать ZIP-архив.
- Перейти в папку \foodgram-project-react\backend и выполнить команды:
```bash
sudo docker build -t <логин на DockerHub>/<название образа для бэкенда, какое хотите)> .
sudo docker login
sudo docker push <логин на DockerHub>/<название образа для бэкенда, которое написали> 
```
- Перейти в папку \foodgram-project-react\frontend и выполнить команды:
```bash
sudo docker build -t <логин на DockerHub>/<название образа для фронтэнда, какое хотите)> .
sudo docker login
sudo docker push <логин на DockerHub>/<название образа для фронтэнда, которое написали> 
```

- Установить docker на сервер:
```bash
sudo apt install docker.io 
```
- Установить docker-compose на сервер:
```bash
sudo apt-get update
sudo apt install docker-compose
```
- Скопировать файл docker-compose.yml и nginx.conf из директории infra на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
```
- Для работы с Workflow добавить в Secrets GitHub переменные окружения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

DOCKER_PASSWORD=<пароль DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID своего телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```
- После деплоя изменений в git, дождитесь выполнения всех Actions.
- Зайдите на боевой сервер и выполните команды:
  * Создаем и применяем миграции
    ```bash
    sudo docker-compose exec backend python manage.py migrate
    ```
  * Подгружаем статику
    ```bash
    sudo docker-compose exec backend python manage.py collectstatic --no-input 
    ```
  * Создать суперпользователя Django
    ```bash
    sudo docker-compose exec backend python manage.py createsuperuser
    ```
  * Загрузить подготовленный список ингредиентов
    ```bash
    sudo docker-compose exec backend python manage.py loaddata ingredients.json
    ```

- Проект будет доступен по вашему IP-адресу.

## Документация к API
API документация доступна по ссылке (создана с помощью redoc):
[http://localhost/api/docs/


## Авторы
[Саркисян М.М.](https://github.com/Mane26) - Python разработчик. Разработала бэкенд и деплой для сервиса Foodgram.  
[Яндекс.Практикум](https://github.com/yandex-praktikum) Фронтенд для сервиса Foodgram.
