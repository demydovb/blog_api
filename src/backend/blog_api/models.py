from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User

from collections import Counter
import re


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

  @receiver(post_save, sender=Post)
  def save_post(sender, instance, created, **kwargs):
    stop_words = ['a', 'the', 'this']
    words = re.findall('\w+', instance.content.lower())
    cnt = Counter()
    for word in words:
      if word not in stop_words:
        cnt[word] += 1

    if created:
      for key, value in cnt.items():
        word, created = Word.objects.get_or_create(word=key)
        words_in_post = PostWord.objects.create(occurrence=value, post=instance, word=word)
    else:
      for old_postword in instance.postword_set.all():
        if str(old_postword.word) not in cnt.keys():
          old_postword.delete()

      for new_postword, value in cnt.items():
        if new_postword not in instance.postword_set.all().values_list('word__word', flat=True):
          word, created = Word.objects.get_or_create(word=new_postword)
          words_in_post = PostWord.objects.create(occurrence=value, post=instance, word=word)
        else:
          word_to_update = PostWord.objects.get(post=instance, word__word=new_postword)
          word_to_update.occurrence = value
          word_to_update.save()
