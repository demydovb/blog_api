from django.urls import path
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_swagger.views import get_swagger_view

from .views import (
  PostListDetailViewSet,
  RegistrationView,
  ProfileView,
  StatisticViewSet,
)


schema_view = get_swagger_view(title='Blog API')

urlpatterns = [
  path('registration/', RegistrationView.as_view(), name='registration'),
  path('auth/login/', obtain_jwt_token, name='auth'),
  path('profile/', ProfileView.as_view(), name='profile'),
  path('docs/', schema_view),
    ]

posts_router = routers.SimpleRouter()
posts_router.register('posts', PostListDetailViewSet)
urlpatterns += posts_router.urls

statistics_router = routers.SimpleRouter()
statistics_router.register('statistics', StatisticViewSet, base_name='statistics')
urlpatterns += statistics_router.urls