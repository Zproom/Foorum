from django.contrib.auth.models import AbstractUser
from django.db import models


# Create a User model with fields for the users the user 
# follows (following), the users following the user (followers),
# and liked posts and comments
class User(AbstractUser):
    following = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="following_users")
    followers = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="follower_users")
    likes = models.ManyToManyField("Post", blank=True)
    comment_likes = models.ManyToManyField("Comment", blank=True)

    # Translate the User model into JSON format
    def serialize(self):
        return {
            "username": self.username,
            "following": [user.username for user in self.following.all()],
            "followers": [user.username for user in self.followers.all()],
            "likes": [post.serialize() for post in self.likes.all()],
            "comment_likes": [comment.serialize() for comment in self.comment_likes.all()]
        }

    # Give the User model a readable name including its username
    def __str__(self):
        return f"{self.username}"


# Create a Post model with fields for a Post's author, board, 
# content, and other properties
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    board = models.ForeignKey("Board", on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=1000)
    image_link = models.URLField(max_length=3000, blank=True)
    num_likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Translate the Post model into JSON format
    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "board": self.board.name,
            "content": self.content,
            "image_link": self.image_link,
            "num_likes": self.num_likes,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p")
        }

    # Give the Post model a readable name including its author and timestamp
    def __str__(self):
        return f"{self.author.username} {self.timestamp}"


# Create a Board model with a field for the Board's name
class Board(models.Model):
    name = models.CharField(max_length=1000)
    description = models.CharField(max_length=8000, blank=True)
    
    # Give the Board model a readable name including its name
    def __str__(self):
        return f"{self.name}"


# Create a Comment model with fields for a Comment's author, post, 
# content, and other properties
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=1000)
    image_link = models.URLField(max_length=3000, blank=True)
    num_likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Translate the Comment model into JSON format
    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "post_id": self.post.id,
            "content": self.content,
            "image_link": self.image_link,
            "num_likes": self.num_likes,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p")
        }

    # Give the Comment model a readable name including its author and timestamp
    def __str__(self):
        return f"{self.author.username} {self.timestamp}"
