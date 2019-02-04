from .celery import app
from collections import Counter
import re

from .models import Word, PostWord, Post



@app.task
def count_words(id, created):
  instance = Post.objects.get(id=id)
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