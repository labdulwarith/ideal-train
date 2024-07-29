from django.forms import ModelForm
from .models import Room, Comment

from django.contrib.auth.models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'members']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

