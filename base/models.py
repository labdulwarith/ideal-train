from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Room(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    members = models.ManyToManyField(User, related_name='members', blank=True)
    open_status = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    suspended_members = models.ManyToManyField(User, related_name='suspended_members', blank=True)
    pending_requests = models.ManyToManyField(User, related_name='pending_requests', blank=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title

class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True, blank=True)
    body = models.TextField()
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    hidden_status = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.body


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    hidden_status = models.BooleanField(default=False)


    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.body


