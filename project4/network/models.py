from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=255)
    likes = models.ManyToManyField(
        User,
        related_name='likers',
    )


class Following(models.Model):
    target = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE
    )
    follower = models.ForeignKey(
        User, 
        related_name='targets',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (('target','follower'),)