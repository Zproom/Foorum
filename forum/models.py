from django.contrib.auth.models import AbstractUser
from django.db import models
from embed_video.fields import EmbedVideoField


# Create a User model with fields for the users the user
# follows (following) and liked posts and comments
class User(AbstractUser):
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="following_users")
    likes = models.ManyToManyField(
        "Post", 
        blank=True,
        related_name="like_users")

    # Translate the User model into JSON format
    def serialize(self):
        return {
            "username": self.username,
            "following": [user.username for user in self.following.all()],
            "likes": [post.serialize() for post in self.likes.all()]
        }

    # Give the User model a readable name including its username
    def __str__(self):
        return f"{self.username}"


# Create a Post model with fields for a Post's author, board,
# content, and other properties. The Post model is also used for
# Comments. The parent field identifies a comment's parent post. 
# Top-level posts have a parent field that is null (parent=None)
class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    board = models.ForeignKey(
        "Board",
        on_delete=models.CASCADE,
        related_name='posts')
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_posts')
    content = models.CharField(max_length=1000)
    thumb = models.ImageField(blank=True)
    video = EmbedVideoField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Translate the Post model into JSON format
    def serialize(self):
        if self.parent is not None:
            parent = self.parent.id
        else:
            parent = None
        if self.thumb:
            url = self.thumb.url
        else:
            url = None
        return {
            "id": self.id,
            "author": self.author.username,
            "board": self.board.name,
            "parent": parent,
            "content": self.content,
            "thumb": url,
            "video": self.video,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p")
        }

    # Give the Post model a readable name including its author and timestamp
    def __str__(self):
        return f"{self.author.username} {self.timestamp}"


# Create a Board model with a field for the Board's name, 
# image, and description
class Board(models.Model):
    name = models.CharField(max_length=1000)
    thumb = models.ImageField(blank=True)
    description = models.CharField(max_length=8000, blank=True)

    # Give the Board model a readable name including its name
    def __str__(self):
        return f"{self.name}"
