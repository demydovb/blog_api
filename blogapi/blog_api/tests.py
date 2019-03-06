import string
import random
from rest_framework.test import APITestCase
from django.urls import reverse

from .utils import get_existing_email

email = get_existing_email('google.com')
register_data = {
  "username": "test_user",
  "password": "test_password",
  "email": email,
  "first_name": "test",
  "last_name": "user",
}

auth_data = {
  'username': register_data['username'],
  'password': register_data['password'],
}

class RegistrationViewTest(APITestCase):
  def setUp(self):
    self.required_data = ['username', 'password', 'email', 'first_name', 'last_name']
    self.register_url = reverse('registration')

  def test_registration(self):
    """
    The registration view should not accept data without
    username/password/email/first_name/last_name
    """
    for key in self.required_data:
      # Try to register user without username/password/email/first_name/last_name.
      key_value = register_data[key]
      del register_data[key]
      response = self.client.post(self.register_url, register_data, format='json')
      self.assertEqual(response.status_code, 400)
      register_data[key] = key_value

    # Try to register user with all data.
    response = self.client.post(self.register_url, register_data, format='json')
    self.assertEqual(response.status_code, 201)

    # Try to register user with same email.
    register_data['username'] = "test_user1"
    response = self.client.post(self.register_url, register_data, format='json')
    self.assertEqual(response.status_code, 400)

    # Try to register user with invalid dummy email.
    register_data['email'] = '{}@google.com'.format(''.join(random.choice(string.ascii_letters) for m in range(20)))
    response = self.client.post(self.register_url, register_data, format='json')
    self.assertEqual(response.status_code, 400)


class AuthViewTest(APITestCase):
  def setUp(self):
    self.auth_url = reverse('auth')
    self.register_url = reverse('registration')

    self.client.post(self.register_url, register_data, format='json')

  def test_auth(self):
    """
    The Auth view should accept valid data and
    decline invalid data
    """

    # Valid data
    response = self.client.post(self.auth_url, auth_data, format='json')
    self.assertEqual(response.status_code, 200)

    # Invalid data
    auth_data_username = auth_data['username']
    auth_data['username'] = "test_user1"
    response = self.client.post(self.auth_url, auth_data, format='json')
    self.assertEqual(response.status_code, 400)
    auth_data['username'] = auth_data_username


class ProfileViewTest(APITestCase):
  def setUp(self):
    self.auth_url = reverse('auth')
    self.register_url = reverse('registration')
    self.profile_url = reverse('profile')
    self.new_first_name = "test_test"

    self.client.post(self.register_url, register_data, format='json')

    response = self.client.post(self.auth_url, auth_data, format='json')
    token = response.data['token']
    self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(token))

  def test_as_auth_user(self):
    """
    The Profile view should  return profile information and can be updated for
    auth user
    """

    response = self.client.get(self.profile_url, format='json')
    self.assertEqual(response.status_code, 200)

    response = self.client.put(self.profile_url, {'first_name': self.new_first_name}, format='json')
    self.assertEqual(response.data.get("first_name", None), self.new_first_name)


  def test_as_not_user(self):
    """
    The Profile view should not return profile information and can not be updated
    for not auth user
    """
    self.client.credentials()
    response = self.client.get(self.profile_url, format='json')
    self.assertEqual(response.status_code, 401)

    response = self.client.put(self.profile_url, {'first_name': self.new_first_name}, format='json')
    self.assertEqual(response.data.get("first_name", None), None)


class PostListDetailViewTest(APITestCase):
  def setUp(self):
    self.auth_url = reverse('auth')
    self.register_url = reverse('registration')
    self.post_url = reverse('post-list')
    self.post = {
      "title": "new_post",
      "content": "new_content"
    }
    self.new_content = "updated_content"

    self.client.post(self.register_url, register_data, format='json')

    response = self.client.post(self.auth_url, auth_data, format='json')
    token = response.data['token']
    self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(token))

  def test_posts(self):
    """
    Auth user should be able to add/update posts, get list of all posts.
    Not auth user - only get list of all posts.
    """

    #Create Post
    response = self.client.post(self.post_url, self.post, format='json')
    self.assertEqual(response.status_code, 201)
    post_id = response.data['id']

    #Update Post
    self.post['content'] = self.new_content
    response = self.client.put(self.post_url + "{}/".format(post_id), self.post, format='json')
    self.assertEqual(response.data.get("content", None), self.new_content)

    #Get all posts
    response = self.client.get(self.post_url, self.post, format='json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)

    # "Log out"
    self.client.credentials()

    #Create Post
    response = self.client.post(self.post_url, self.post, format='json')
    self.assertEqual(response.status_code, 401)

    #Get all posts
    response = self.client.get(self.post_url, self.post, format='json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)

  def test_likes(self):
    """
    Any auth user should be able to increase/decrease like counter
    """
    # Create Post
    response = self.client.post(self.post_url, self.post, format='json')
    post_id = response.data['id']

    # Like Post
    response = self.client.post(self.post_url + "{}/like/".format(post_id), format='json')
    self.assertEqual(response.data.get("like_counter", None), 1)

    # Unlike Post
    response = self.client.post(self.post_url + "{}/like/".format(post_id), format='json')
    self.assertEqual(response.data.get("like_counter", None), 0)

