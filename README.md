# Как запустить проект?

> <https://stackoverflow.com/a/55954355> <- Тут решение проблемы с mysqlclient `mysqlclient 1.4.3 or newer is required; you have 1.0.3.`

Вот путь до того файла: `myenv/lib/python3.11/site-packages/django/db/backends/mysql/base.py`

### 1. Сначала создаем виртуальное окружение Python

```sh
python -m venv myenv      # создание виртуальной среды
source myenv/bin/activate
```

### 2. Установите Poetry, если он еще не установлен. Как это сделать можно найти в документации <https://python-poetry.org/docs/>

### Запустите установку зависимостей

```sh
poetry install
```

> Добавить зависимости можно используя команду `add`

```sh
poetry add <package>
```

Настройка авто-форматирования кода

1. Установите `ms-python.autopep8` расширение для VS Code
2. Установите его как форматер `.py` файлов по умолчанию

```json
{
  // ...Other configs
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.autopep8"
  }
}
```

### База данных mysql

Гайд по установке mysql для работы проекта: <https://adminway.ru/mac-os-install-mysql?ysclid=lh9dx4vyth55406236>

Конфигурация базы данных происходит по переменным `MYSQL_DB_USER` и `MYSQL_DB_PASSWORD`. Эти переменные должны быть указаны в файле `environment.py`, который нужно создать в корне проекта.

Подготовка базы данных:

1. Перейдите в интерактивный режим с пользователем которого создали

```sh
mysql -u root -pmysql -u root -p
```

2. Создайте необходимые таблицы (не уверен о надобности 2-рой команды)

```sql
CREATE DATABASE persona;
USE persona;
CREATE DATABASE personal_area_personaldata;
```

3. Запустить миграции

```sh
myenv/bin/python manage.py migrate
```

4. Запустить сервер

```sh
myenv/bin/python manage.py runserver
```
