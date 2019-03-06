from django.contrib import admin

from .models import Post, PostWord, Profile, Word

admin.site.register(Post)
admin.site.register(PostWord)
admin.site.register(Profile)
admin.site.register(Word)
