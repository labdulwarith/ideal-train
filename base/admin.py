from django.contrib import admin
from .models import Room, Message, Comment, Event, Poll, Choice
# Register your models here.


admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Poll)
admin.site.register(Event)
admin.site.register(Choice)
