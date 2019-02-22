from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Post, Profile, PostWord
from .utils import check_if_email_exists


class PostSerializerMixin():
  def get_like_counter(self, obj):
    return obj.liked_users.count()


class PostSerializer(serializers.ModelSerializer, PostSerializerMixin):
  """ Model Serializer for  List Post """

  author = serializers.CharField(source='author.username', required=False)
  like_counter = serializers.SerializerMethodField()

  class Meta:
    model = Post
    fields = ('author', 'title', 'published', 'updated', 'id', 'like_counter')


  def create(self, validated_data):
    if not self.context['request'].data.get('content', False):
      raise serializers.ValidationError("You cannot post new article without content")

    post = Post.objects.create(
      title=validated_data['title'],
      content=self.context['request'].data['content'],
      author = self.context['request'].user
    )

    return post


class PostDetailSerializer(serializers.ModelSerializer, PostSerializerMixin):
  """ Model Serializer for Detail Post """

  author = serializers.CharField(source='author.username', required=False)
  like_counter = serializers.SerializerMethodField()

  class Meta:
    model = Post
    fields = ('author', 'title', 'content', 'published', 'updated', 'id', 'like_counter')
    extra_kwargs = {
      'author': {'read_only': True},
      'title': {'required': False},
      'content': {'required': False},
    }


  def update(self, instance, validated_data):
    for attr, value in validated_data.items():
      setattr(instance, attr, value)

    instance.save()
    return instance

class AuthorSerializer(serializers.ModelSerializer):
  """ Model Serializer for Author """

  class Meta:
    model = Profile
    fields = ('bio', 'location')


class UserSerializer(serializers.ModelSerializer):
  """ Model Serializer for User """
  profile = AuthorSerializer(required=False)
  password = serializers.CharField(write_only=True, required=False)

  class Meta:
    model = User
    fields = ('username', 'password', 'first_name', 'last_name', 'email', 'profile')
    extra_kwargs = {
      'username': {'required': False},
    }

  def create(self, validated_data):
    user = User.objects.create_user(
      username=validated_data['username'],
      password=validated_data['password'],
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name'],
      email=validated_data['email'],
    )

    if validated_data.get("profile", False):
      profile = Profile.objects.create(**validated_data["profile"], user=user)
      user.profile = profile
      user.save()
    else:
      from .tasks import get_profile_info_from_clearbit
      get_profile_info_from_clearbit.delay(user.pk, validated_data['email'])
    return user

  def update(self, instance, validated_data):
    if validated_data.get('username', False):
      raise serializers.ValidationError("You cannot change username")

    if validated_data.get('password', False):
      instance.set_password(validated_data['password'])
      del validated_data['password']

    if validated_data.get('profile', False):
      for attr, value in validated_data['profile'].items():
        if not hasattr(instance, 'profile'):
          profile = Profile.objects.create(user_id=instance.id)
          instance.save()
        setattr(instance.profile, attr, value)
      del validated_data['profile']

    for attr, value in validated_data.items():
      setattr(instance, attr, value)

    if hasattr(instance, 'profile'):
      instance.profile.save()
    instance.save()
    return instance

  def validate_email(self, value):
    """ Validate during creating object if email is not already taken by another user and email is present in
        emailhunter database """
    if not self.instance and User.objects.filter(email=value).exists() :
      raise serializers.ValidationError("User with email {}  is already registered in our site".format(value))

    if not check_if_email_exists(value):
      raise serializers.ValidationError("Email is invalid. Please, enter valid corporate email. ".format(value))
    return value

  def validate(self, data):
    """ Validate during creating object if all needed properties are passed ( for updating they are not required)"""
    if not self.instance and ('username' not in data or 'password' not in data or 'email' not in data or
                                  'first_name' not in data or 'last_name' not in data):
      raise serializers.ValidationError("All this fields must be input: username, password, email, first_name, last_name")
    return data


class WordsInPostSerializer(serializers.ModelSerializer):
  """ Model Serializer for all unique words in post """

  word = serializers.CharField(source='word.word')
  class Meta:
    model = PostWord
    fields = ('word', 'occurrence')

class CalculatedWordsFromAllSerializer(serializers.Serializer):
  """ Serializer for calculated words from all posts """
  unique_word = serializers.CharField(max_length=200)
  occurrence = serializers.IntegerField()

  class Meta:
    fields = ('unique_word', 'occurrence')