from django.contrib import admin

from .models import User, Post, Board, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Board)
admin.site.register(Comment)
