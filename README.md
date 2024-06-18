# sunny_backend
Бекэнд для проекта "Солнечный" город Екатеринбург"</br>
[![code review](https://github.com/SunnyEkb/sunny_backend/actions/workflows/sunny_ekb.yaml/badge.svg)](https://github.com/SunnyEkb/sunny_backend/actions/workflows/sunny_ekb.yaml/)
[![prod deploy](https://github.com/SunnyEkb/sunny_backend/actions/workflows/prod_deploy.yaml/badge.svg)](https://github.com/SunnyEkb/sunny_backend/actions/workflows/prod_deploy.yaml/)

## Описание
Web приложение для улучшения качества жизни резидентов района "Солнечный" города Екатеринбург

## Для разработчиков:

### Приложения:
- _config_: общие настройки проекта;

- users: управление пользователями.

### Пример файла с переменными среды:
".env.example" в корневой папке проекта:

### Линтер:
`black`

### Pre-commit:
Настроен pre-commit для проверки оформления кода.
Для проверки кода перед выполнением операции commit, выполнить команду:

```
pre-commit run --all-files
```

## Как запустить проект:

Клонировать проект
```
git clone https://github.com:SunnyEkb/sunny_backend.git
```

Переименовать файл .env.example и изменить содержимое на актуальные данные.
```
mv .env.example .env
```

### 1) Запуск проекта на локальной машине:

Создать виртуальное окружение:
```
py -3 -m venv venv
```

Активировать виртуальное окружение:
```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

В папке с файлом manage.py (./src) выполнить следующие команды для миграций:
```
python manage.py migrate
```

Создать суперюзера:
```
python manage.py createsuperuser
```

Запустить проект:
```
python manage.py runserver
```

### 2) Запуск через Docker:
Запустить контейнер c проектом
```
docker-compose up -d
```

Выполнить миграции:
```
docker-compose exec backend python manage.py migrate
```

Проект будет доступен на 8000 порту.
Swager доступен по адресу:
```
http://localhost:8000/api/v1/docs/
```

Если отсутствуют статические файлы, то выполнить
```
docker-compose exec backend python manage.py collectstatic --no-input
```

## Системные требования
### Python==3.12

## Стек
### Django
### Django REST Framework
### PosrgreSQL
