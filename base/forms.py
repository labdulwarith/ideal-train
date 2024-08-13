from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.forms import ModelForm, DateTimeInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Room, Comment, Poll, Message, Event, Choice



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
        fields = ['question', 'starts_at', 'expires_at']
        widgets = {
            'starts_at': DateTimeInput(attrs={
                'type': 'datetime-local'
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
                'type': 'datetime-local'
            }),
            'expires_at': DateTimeInput(attrs={
                'type': 'datetime-local'
            })
        }


class ChoiceForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['text']


