# Как запустить проект?

### 1. Сначала создаем виртуальное окружение Python

```sh
python -m venv myenv
source myenv/bin/activate
```

### 3. Запустите установку зависимостей

```sh
pip install -r reqs.txt
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
