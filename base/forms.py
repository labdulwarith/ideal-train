from django.forms import ModelForm, DateTimeInput
from .models import Room, Comment, Poll, Message, Event

from django.contrib.auth.models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'members', 'suspended_members', 'pending_requests']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        exclude = ['likes', 'author', 'room', 'hidden_status']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

class PollForm(ModelForm):
    class Meta:
        model = Poll
        fields = '__all__'
        exclude = ['created_by', 'voted_users', 'room']
        widgets = {
            'starts_at': DateTimeInput(attrs={
                'type':'datetime-local'
            }),
            'expires_at': DateTimeInput(attrs={
                'type': 'datetime-local'
            })
        }


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ['created_by', 'room', 'accepted', 'rejected']
        widgets = {
            'starts_at': DateTimeInput(attrs={
                'type':'datetime-local'
            }),
            'expires_at': DateTimeInput(attrs={
                'type': 'datetime-local'
            })
        }

