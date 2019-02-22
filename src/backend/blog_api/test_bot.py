import requests
import string
import random
import os
import json
import threading
from django.urls import reverse

from .utils import get_existing_emails

BASE_URL = 'http://localhost:8000'
HEADERS={'content-type': 'application/json'}
emails = []
tokens = []
posts = []

def generate_random_string():
  return ''.join(random.choice(string.ascii_letters) for m in range(6))


def generate_emails():
  print("Generating emails...")
  _emais = get_existing_emails('google.com')
  for email in _emais:
    emails.append(email['value'])

def create_user_and_posts(i):
  print("Creating user #{}...".format(i))
  register_data = {
    "username": generate_random_string(),
    "password": generate_random_string(),
    "email": emails.pop(),
    "first_name": generate_random_string(),
    "last_name": generate_random_string(),
  }
  r = requests.post(BASE_URL + reverse('registration'), json.dumps(register_data), headers=HEADERS)

  print("User {} creating posts...".format(register_data['username']))
  for i in range(int(os.getenv('BOT_CONF_MAX_POSTS_PER_USER'))):
    post_content = {
      "title": generate_random_string(),
      "content": generate_random_string(),
    }
    auth_data = {
      'username': register_data['username'],
      'password': register_data['password'],
    }
    response = requests.post(BASE_URL + reverse('auth'), json.dumps(auth_data), headers=HEADERS)
    token = response.json()['token']
    tokens.append(token)
    headers = {'Authorization':'JWT {0}'.format(token), **HEADERS}
    response = requests.post(BASE_URL + reverse('post-list'), json.dumps(post_content), headers=headers)
    posts.append(response.json()['id'])


def generate_posts():
  threads = []
  for i in range(1, int(os.getenv('BOT_CONF_NUMBER_OF_USERS'))+1):
    my_thread = threading.Thread(target=create_user_and_posts, args=(i,))
    threads.append(my_thread)
    my_thread.start()

  for t in threads:
    t.join()


def like_posts(token, posts):
  for _ in range(int(os.getenv('BOT_CONF_MAX_LIKES_PER_USER'))):
    post_to_like = posts.pop()
    headers = {'Authorization': 'JWT {0}'.format(token), **HEADERS}
    requests.post("{}{}/like/".format(BASE_URL + reverse('post-list'), post_to_like), headers=headers)

# If you use postgres or mysql, it is possible to have multiple threads that likes posts, but it's impossible in
# SQLite which is currently used

# def generate_liked_posts():
#   print("Users likes posts...")
#   for token in tokens:
#     posts_to_like = posts[::]
#     random.shuffle(posts_to_like)
#     my_thread = threading.Thread(target=like_posts, args=(token, posts_to_like))
#     my_thread.start()

def generate_liked_posts():
  print("Users likes posts...")
  for token in tokens:
    posts_to_like = posts[::]
    random.shuffle(posts_to_like)
    like_posts(token, posts_to_like)


def get_result():
  print("\n\n RESULT:\n")
  response = requests.get(BASE_URL +reverse('post-list'))
  print(response.json())

def main():
  generate_emails()
  generate_posts()
  generate_liked_posts()
  get_result()

if __name__ == "__main__":
  main()