from rest_framework import generics, permissions, viewsets, decorators, response
from django.contrib.auth.models import User
from django.db.models import Sum, F

from .models import Post, PostWord
from .serializers import PostSerializer, PostDetailSerializer, UserSerializer, WordsInPostSerializer, CalculatedWordsFromAllSerializer
from .permissions import IsOwnerOrReadOnly


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


class PostListViewSet(viewsets.ModelViewSet):
  queryset = Post.objects.order_by("-published")
  serializer_class = PostSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

  def get_permissions(self):
    """
    Instantiates and returns the list of permissions that this view requires.
    """
    if self.action == 'list' or self.action == 'retrieve':
      permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    elif self.action =='create':
      permission_classes = [permissions.IsAuthenticated]
    else:
      permission_classes = [IsOwnerOrReadOnly]
    return [permission() for permission in permission_classes]

  def list(self, request, *args, **kwargs):
    user_to_filter = request.query_params.get('username', None)
    if user_to_filter:
      posts_by_user = Post.objects.order_by("-published").filter(author__username=user_to_filter)
      if not posts_by_user:
        return response.Response("There are not {}'s posts.".format(user_to_filter))
      serializer = PostSerializer(posts_by_user, many=True)
      return response.Response(serializer.data)
    return super().list(request, *args, **kwargs)


  def retrieve(self, request, *args, **kwargs):
    self.serializer_class = PostDetailSerializer
    return super().retrieve(request, *args, **kwargs)


  def update(self, request, *args, **kwargs):
    self.serializer_class = PostDetailSerializer
    return super().update(request, *args, **kwargs)

  @decorators.action(methods=['get'], detail=False, url_path='my-posts')
  def retrieve_my_posts(self, request, pk=None):
    my_posts =  Post.objects.order_by("-published").filter(author=self.request.user)
    serializer = PostSerializer(my_posts, many=True)
    return response.Response(serializer.data)


class StatisticViewSet(viewsets.ViewSet):
  def list(self, request):
    queryset = PostWord.objects.values(unique_word=F('word__word')).annotate(occurrence=Sum('occurrence'))

    serializer = CalculatedWordsFromAllSerializer(queryset, many=True)
    print(serializer.data)
    return response.Response(serializer.data)

  def retrieve(self, request, pk=None):
    queryset = PostWord.objects.filter(post__id=pk)
    serializer = WordsInPostSerializer(queryset, many=True)
    return response.Response(serializer.data)

