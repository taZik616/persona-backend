# Как запустить проект?

А это очень легко, просто с помощью `docker-compose` 😊

## Настройте конфиги

Создайте в корне проекта и настройте `environment.py` файл(см. `environment.example.py`)

> Для представления `db` в файле `docker-compose.yml` установите env переменные

## Запускаем эту команду в корне проекта

```sh
sudo docker compose up --build -d
# или
sudo docker compose -f docker-compose-debug.yml up --build -d
```

Если при запуске возникла ошибка `failed to solve: error getting credentials - err: exit status 1, out: \`\``, то запустите команду:

```sh
rm ~/.docker/config.json
```

## Server setup

<https://docs.docker.com/engine/install/ubuntu/>

Команды для создания супер пользователя

```sh
docker exec -it CONTAINER_ID bash

python manage.py createsuperuser
```

> `cmd + D` - выйти

## Чистка docker

```sh
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
docker image prune
docker builder prune
docker container prune
docker system prune
docker rmi --force $(docker images -aq)
docker system prune --all --force --volumes
```

## Запуск без Docker

### 1. Запустите установку зависимостей

```sh
pip install -r reqs.txt
```

### 2. Запустить миграции

```sh
python manage.py makemigrations api
python manage.py makemigrations
python manage.py migrate
```

### 3. Установите и запустите memcached

С сайта <https://memcached.org/downloads>

Или с помощью homebrew:

```sh
brew install memcached
```

Запустите локально процесс memcached:

```sh
memcached -m 64 -p 12321 -u root -l 127.0.0.1
```

`-m 64` - кол-во используемой памяти(МБ)
`-l 127.0.0.1` - расположение сервиса
`-p 1121` - порт

> Ну там еще настройте postgresql и celery... Кароч качайте докер лучше

### N. Запустите сервер

```sh
python manage.py runserver
```
