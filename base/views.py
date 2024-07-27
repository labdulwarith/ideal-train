from django.shortcuts import render
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

from .models import Room, Message, Comment
# Create your views here.

def home(request):
    rooms = Room.objects.all()[:3]
    rooms_count = rooms.count()
    context = {
        'rooms': rooms,
        'rooms_count': rooms_count
    }
    return render(request, 'base/home.html', context)

def login_page(request):
    pass

def register_page(request):
    pass

def logout(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        #Do somethin
        pass

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render('delete-room', 'base/delete_room.html', {'obj': room})

def user_profile(request):
    pass

@login_required(login_url='login')
def create_message():
    pass

@login_required(login_url='login')
def create_comment(request):
    pass


