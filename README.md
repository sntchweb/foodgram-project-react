# Foodgram - проект для публикации рецептов.
## Описание:
«Foodgram» - это онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в «Избранное», а также скачивать список продуктов, необходимых для приготовления одного или нескольких блюд.
##  Основные возможности:
-   Просматривать рецепты на главной странице.
-   Просматривать отдельные страницы рецептов.
-   Просматривать страницы пользователей.
-   Фильтровать рецепты по тегам.
-   Входить в систему под логином и паролем.
-   Менять свой пароль.
-   Создавать/редактировать/удалять собственные рецепты.
-   Просматривать страницы пользователей.
-   Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

## Как развернуть проект:

* Установите Docker и Docker-Compose.
* Клонируйте репозиторий командой:
`git clone git@github.com:sntchweb/foodgram-project-react.git`
* Создайте в директории /foodgram-project-react/ файл `.env` с переменными окружения.
```
POSTGRES_DB=django
POSTGRES_USER=django
POSTGRES_PASSWORD=django
DB_NAME=django
DB_HOST=db
DB_PORT=5432
```
* Откройте терминал и запустите сборку docker-контейнеров командой:  
`sudo docker-compose up -d`.  
* Примените миграции:  
`sudo docker compose -f docker-compose.yml exec backend python manage.py migrate`  
* Соберите и скопируйте статику:  
`sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic`  
`sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /static/static/`

Проект будет доступен по адресу: `http://localhost:8000/`  
* Для загрузки всех ингредиентов в базу воспользуйтесь модулем `Import` в разделе ингредиентов админки или командой:  
`sudo docker compose -f docker-compose.yml exec backend python manage.py load_ingredients`

* Для создания суперпользователя воспользуйтесь командой:
`sudo docker compose -f docker-compose.yml exec backend python manage.py createsuperuser`


## Стек технологий:
* [Pyhton](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [Django Rest Framework](https://www.django-rest-framework.org/)
* [PostgreSQL](https://www.postgresql.org/)
* [Docker](https://www.docker.com/)
* [Nginx](https://nginx.org/ru/)
* [Gunicorn](https://gunicorn.org/)

## Автор:
Лашин Артём
