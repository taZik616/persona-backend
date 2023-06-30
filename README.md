# Как запустить проект?

А это очень легко, просто с помощью `docker-compose` 😊

## Настройте конфиги

Создайте в корне проекта и настройте `environment.py` файл, со всеми необходимыми переменными

## Запускаем эту команду в корне проекта

```sh
docker compose up --build -d
# или
sudo docker compose up --build -d
```

Если при запуске с `sudo` возникла ошибка `failed to solve: error getting credentials - err: exit status 1, out: \`\``, то запустите команду:

```sh
rm ~/.docker/config.json
```

## Server setup

<https://docs.docker.com/engine/install/ubuntu/>

Команды для создания супер пользователя при первом развертывании

```sh
docker exec -it CONTAINER_ID bash

python manage.py createsuperuser
```

> `cmd + D` - выйти после создания супер-пользователя

`CONTAINER_ID` можно узнать запустив команду `docker ps`, нужен процесс с названием `app`

## Чистка docker - если хотите заново развернуть backend

> Например если совершены миграции БД, которые поломали проект

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

Лучший вариант

```sh
sudo -s
systemctl stop docker
rm -rf /var/lib/docker
systemctl start docker
exit
```
