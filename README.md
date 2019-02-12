# Blog application (API) #
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
1) Start redis server: `redis-server` (in new terminal)
2) Change directory to **/blog_api/src/backend** `cd ./blog_api/src/backend`
3) Start celery: `celery worker -A blog_api --loglevel=debug --concurrency=1` ( in new terminal)
4) Apply migrations: `python manage.py migrate`
5) Start server: `python manage.py runserver`


Load db dumb (not required):
  `python manage.py loaddata  db.json`
  
Running tests:
  `python manage.py test`

**API Documentation** - http://localhost:8000/docs/
