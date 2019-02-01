from rest_framework import generics, permissions
from django.contrib.auth.models import User

from .models import Post
from .serializers import PostSerializer, UserSerializer

class BlogPostListView(generics.ListCreateAPIView):
  """ View to get list of blog posts

  get: return list of blog posts.
  """
  queryset = Post.objects.order_by("-published")
  serializer_class = PostSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )



class RegistrationView(generics.CreateAPIView):
  """ View to register profile

  post: register profile.
  """
  queryset = User.objects.all()
  serializer_class = UserSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
  """ View to update profile

  post: register author.
  """
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (permissions.IsAuthenticated, )


  def get_object(self, queryset=None):
    obj = self.request.user
    return obj


