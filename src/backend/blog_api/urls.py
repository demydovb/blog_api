from django.urls import path
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from .views import (
  PostListViewSet,
  RegistrationView,
  ProfileView,
  StatisticViewSet,
)

urlpatterns = [
  path('registration/', RegistrationView.as_view(), name='registration'),
  path('auth/login/', obtain_jwt_token, name='auth'),
  path('profile/', ProfileView.as_view(), name='profile'),
    ]

posts_router = routers.SimpleRouter()
posts_router.register('posts', PostListViewSet)
urlpatterns += posts_router.urls

statistics_router = routers.SimpleRouter()
statistics_router.register('statistics', StatisticViewSet, base_name='statistics')
urlpatterns += statistics_router.urls