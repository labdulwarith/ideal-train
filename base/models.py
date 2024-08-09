from enum import Enum
from django.contrib.auth.models import User
from django import forms
from django.db import models
from django.utils import timezone
# Create your models here.

class Room(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    admins = models.ManyToManyField(User, related_name='admin_rooms', blank=True)
    members = models.ManyToManyField(User, related_name='member_rooms', blank=True)
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
    likes = models.ManyToManyField(User, related_name='liked_messages', blank=True)
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

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    rejected = models.ManyToManyField(User, related_name='rejected_events', blank=True)
    accepted = models.ManyToManyField(User, related_name='accepted_events', blank=True)
    starts_at = models.DateTimeField('Start time of event')
    expires_at = models.DateTimeField('End time of event')


    def __str__(self):
        return self.title

    def has_started(self):
        return timezone.now() > self.starts_at

    def has_ended(self):
        return timezone.now() > self.expires_at

    class Meta:
        ordering = ['expires_at', '-starts_at']

class Poll(models.Model):
    question = models.CharField(max_length=200)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    starts_at = models.DateTimeField('Start time of poll')
    expires_at = models.DateTimeField('End time of voting')
    voted_users = models.ManyToManyField(User, related_name='voted_polls', blank=True)

    def __str__(self):
        return self.question

    def has_started(self):
        return timezone.now() > self.starts_at

    def has_ended(self):
        return timezone.now() > self.expires_at

    class Meta:
        ordering = ['expires_at', '-starts_at']

class Choice(models.Model):
    text = models.CharField(max_length=200)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.text
    class Meta:
        ordering = ['votes', '-text']

ACTION_TYPE = (
    ('c', 'commented'),
    ('l', 'liked')
)

class Notification(models.Model):
    read_status = models.BooleanField(default=False)
    action_by = models.ForeignKey(User, related_name='action_by', on_delete=models.CASCADE)
    action_to = models.ForeignKey(User, related_name='action_to', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    action_type = models.CharField(
        max_length=1,
        choices=ACTION_TYPE,
        default='c',
        help_text='Description of notification'
    )

class AdminNotification(models.Model):
    read_status = models.BooleanField(default=False)
    action_by = models.ForeignKey(User, related_name='admin_action_by', on_delete=models.CASCADE)
    action_to = models.ForeignKey(User, related_name='admin_action_to', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    action_type = models.CharField(
        max_length=1,
        choices=ACTION_TYPE,
        default='c',
        help_text='Description of admin notification'
    )

