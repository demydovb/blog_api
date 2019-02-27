# Blog application for corporate clients (API) #
Registered users can add/update new posts, update personal information.
All users can read posts and search posts by selected user.
All users can see unique word's occurrence in selected posts or in all posts (Occurrence ofunique words is being calculated in background during saving (Celery + Redis))


**Pre-requirements:**
  - python3.6
  - redis
  - celery

Install requirements:
  `pip install requirements.txt`

Start app:
1) Create .env file in root directory and populate it with data:

>  EMAILHUNTERS_KEY=XXX<br />
>  CLEARBIT_KEY=XXX<br />
>  BOT_CONF_NUMBER_OF_USERS=INT<br />
>  BOT_CONF_MAX_POSTS_PER_USER=INT<br />
>  BOT_CONF_MAX_LIKES_PER_USER=INT<br />
 

2) Start redis server: `redis-server` (in new terminal)
3) Change directory to **/blog_api/src/backend** `cd ./src/backend`
4) Start celery: `celery worker -A celery_tasks --loglevel=debug` ( in new terminal)
5) Apply migrations: `python manage.py migrate`
6) Start server: `python manage.py runserver`

  
Running tests:
  `python manage.py test`

For populating DB with users and liked posts ( just for demo) i created script for it. 
Start script:
1) Enter shell: `python manage.py shell`
2) Run commands in the shell: 
- `from blog_api.test_bot import main`
- `main()`
3) In ouput you will get unstructured data. For better view after finishing scripts just open main page in your browser.
![Screenshot](https://b.radikal.ru/b13/1902/5e/4751cc4f8be0.png "Screenshot")

**API Documentation** - http://localhost:8000/docs/
