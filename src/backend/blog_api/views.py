from rest_framework import generics, permissions, viewsets, decorators, response
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.shortcuts import  get_object_or_404

from .models import Post, PostWord
from .serializers import PostSerializer, PostDetailSerializer, UserSerializer, WordsInPostSerializer, CalculatedWordsFromAllSerializer
from .permissions import IsOwnerOrReadOnly


class RegistrationView(generics.CreateAPIView):
  """ View to register profile

  post: Register profile.
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


class PostListDetailViewSet(viewsets.ModelViewSet):
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
    """
    get: Get all posts. To get posts from specific user, add parameter ?username=<username>.
    """
    user_to_filter = request.query_params.get('username', None)
    if user_to_filter:
      posts_by_user = Post.objects.order_by("-published").filter(author__username=user_to_filter)
      if not posts_by_user:
        return response.Response("There are not {}'s posts.".format(user_to_filter))
      serializer = PostSerializer(posts_by_user, many=True)
      return response.Response(serializer.data)
    return super().list(request, *args, **kwargs)


  def retrieve(self, request, *args, **kwargs):
    """
    get: Retrieve specific post.
    """
    self.serializer_class = PostDetailSerializer
    return super().retrieve(request, *args, **kwargs)


  def update(self, request, *args, **kwargs):
    """
    put: Update specific post.
    """
    self.serializer_class = PostDetailSerializer
    return super().update(request, *args, **kwargs)

  def partial_update(self, request, *args, **kwargs):
    """
    patch: Update specific post.
    """
    self.serializer_class = PostDetailSerializer
    return super().update(request, *args, **kwargs)

  def destroy(self, request, *args, **kwargs):
    """
    delete: Delete specific post.
    """
    self.serializer_class = PostDetailSerializer
    return super().destroy(request, *args, **kwargs)

  @decorators.action(methods=['get'], detail=False, url_path='my-posts')
  def retrieve_my_posts(self, request, pk=None):
    """
    get: Get all posts from authenticated user.
    """
    my_posts =  Post.objects.order_by("-published").filter(author=self.request.user)
    serializer = PostSerializer(my_posts, many=True)
    return response.Response(serializer.data)

  @decorators.action(methods=['post'], detail=True, url_path='like', permission_classes=[permissions.IsAuthenticated])
  def like_post(self, request, pk=None):
    """
    post: Like specific post.
    """
    liked_post = get_object_or_404(Post, pk=pk)
    user = self.request.user
    if user not in liked_post.liked_users.all():
      liked_post.liked_users.add(self.request.user)
    else:
      liked_post.liked_users.remove(self.request.user)
    liked_post.save()
    serializer = PostDetailSerializer(liked_post)
    return response.Response(serializer.data)

class StatisticViewSet(viewsets.ViewSet):
  def list(self, request):
    """
    get: Get word's occurrence from all posts.
    """
    queryset = PostWord.objects.values(unique_word=F('word__word')).annotate(occurrence=Sum('occurrence'))

    serializer = CalculatedWordsFromAllSerializer(queryset, many=True)
    return response.Response(serializer.data)

  def retrieve(self, request, pk=None):
    """
    get: Get word's occurrence from specific post.
    """
    queryset = PostWord.objects.filter(post__id=pk)
    if Post.objects.filter(id = pk).exists() and not PostWord.objects.filter(post__id=pk).exists():
      return response.Response("Word's count is being calculated for this post, try in a few seconds...")
    serializer = WordsInPostSerializer(queryset, many=True)
    return response.Response(serializer.data)

