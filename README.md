# Как запустить проект?

### 1. Сначала создаем виртуальное окружение Python

```sh
python -m venv myenv
source myenv/bin/activate
```

### 2. Установите Poetry, если он еще не установлен. Как это сделать можно найти в документации <https://python-poetry.org/docs/>

### 3. Запустите установку зависимостей

```sh
poetry install
```

> Добавить зависимости можно используя команду `add`

```sh
poetry add <package>
```

### 4. Запустить миграции

```sh
myenv/bin/python manage.py makemigrations api
myenv/bin/python manage.py makemigrations
myenv/bin/python manage.py migrate
```

### 5. Установите и запустите memcached

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

### Добавьте значения в файл environment.py

Создайте в той же директории, где находиться `environment.example.py`, файл `environment.py` с переменной `MEMCACHED_LOCATION`:

```py
MEMCACHED_LOCATION = 'LOCATION:PORT'
```

### 6. Запустите сервер

```sh
myenv/bin/python manage.py runserver
```

### База данных mysql(не актуально)

Гайд по установке mysql для работы проекта: <https://adminway.ru/mac-os-install-mysql?ysclid=lh9dx4vyth55406236>

Конфигурация базы данных происходит по переменным `MYSQL_DB_USER` и `MYSQL_DB_PASSWORD`. Эти переменные должны быть указаны в файле `environment.py`, который нужно создать в корне проекта.

Подготовка базы данных:

1. Перейдите в интерактивный режим с пользователем которого создали

```sh
mysql -u root -p
```

2. Создайте необходимые таблицы (не уверен о надобности 2-рой команды)

```sql
CREATE DATABASE persona;
USE persona;
CREATE DATABASE personal_area_personaldata;
```

> <https://stackoverflow.com/a/55954355> <- Тут решение проблемы с mysqlclient `mysqlclient 1.4.3 or newer is required; you have 1.0.3.`

Вот путь до того файла: `myenv/lib/python3.11/site-packages/django/db/backends/mysql/base.py`
