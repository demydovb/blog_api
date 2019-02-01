from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Post, Profile


class PostSerializer(serializers.ModelSerializer):
  """ Model Serializer for Post """

  author = serializers.CharField(source='author.username', required=False)
  class Meta:
    model = Post
    fields = ('title', 'content', 'published', 'updated', 'author')


  def create(self, validated_data):
    post = Post.objects.create(
      title=validated_data['title'],
      content=validated_data['content'],
      author = self.context['request'].user
    )

    return post


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
    """ Validate during creating object if email is not already taken by another user"""
    if not self.instance and User.objects.filter(email=value).exists() :
      raise serializers.ValidationError("User with email {}  is already registered in our site".format(value))
    return value

  def validate(self, data):
    """ Validate during creating object if all needed properties are passed ( for updating they are not required)"""
    if not self.instance and ('username' not in data or 'password' not in data or 'email' not in data or
                                  'first_name' not in data or 'last_name' not in data):
      raise serializers.ValidationError("All this fields must be input: username, password, email, first_name, last_name")
    return data


