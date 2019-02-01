from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  bio = models.TextField(max_length=500, blank=True)
  location = models.CharField(max_length=30, blank=True)

  def __str__(self):
    return "{}'s profile".format(self.user.username)


class Post(models.Model):
  title = models.CharField(max_length=70, blank=False, unique=True, null=False)
  content = models.TextField(blank=False, null=False)
  published = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

  def __str__(self):
    return self.title


class Word(models.Model):
  word = models.CharField(max_length=50, blank=False, null=False)

  def __str__(self):
    return self.word


class PostWord(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE)
  word = models.ForeignKey(Word, on_delete=models.CASCADE)
  occurrence = models.IntegerField(blank=False, null=False)

  def __str__(self):
    return "{} from post {}:{} occurrences".format(self.word.word, self.post.title, self.occurrence)

