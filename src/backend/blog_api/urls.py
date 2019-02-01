from django.urls import include, path
from rest_framework_jwt.views import obtain_jwt_token

from .views import (
  BlogPostListView,
  RegistrationView,
  ProfileView,
  # AuthView,
)

urlpatterns = [
  path('', BlogPostListView.as_view(), name='posts'),
  path('registration', RegistrationView.as_view(), name='registration'),
  path('auth/login', obtain_jwt_token, name='auth'),
  path('profile', ProfileView.as_view(), name='profile'),
    ]

