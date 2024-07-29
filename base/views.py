from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .forms import RoomForm, CommentForm
from .models import Room, Message, Comment
# Create your views here.

def home(request):
    my_rooms = []
    if request.user.is_authenticated:
        #TODO: Return rooms where user logged in user is a member
        my_rooms = Room.objects.filter(members=request.user)
        open_rooms = Room.objects.exclude(members=request.user).filter(open_status=True)
        closed_rooms = Room.objects.exclude(members=request.user).filter(open_status=False)
    else:
        open_rooms = Room.objects.filter(open_status=True)
        closed_rooms = Room.objects.filter(open_status=False)

    rooms_count = Room.objects.all().count()

    context = {
        'my_rooms': my_rooms,
        'open_rooms': open_rooms,
        'closed_rooms': closed_rooms,
        'rooms_count': rooms_count
    }
    return render(request, 'base/home.html', context)

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def register_page(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    return render(request, 'base/login_register.html', {'form': form})


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()

    if request.method == 'POST':
        pass
#TODO: define how to save new room

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def room(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        user = User.objects.get(id=request.POST.get('user'))
        if action == 'accept':
            room.pending_requests.remove(user)
            room.members.add(user)
        else:
            room.pending_requests.remove(user)
        room.save()
        redirect('room', pk=room.id)

    room_messages = room.message_set.filter(hidden_status=False)
    hidden_messages = room.message_set.filter(hidden_status=True)
    members = room.members.all()
    members_count = members.count()
    pending_requests = room.pending_requests.all()
    suspended_members = room.suspended_members.all()

    if not request.user in room.members.all():
        return HttpResponse('You are not allowed here')

    context = {
        'room': room,
        'room_messages': room_messages,
        'hidden_messages': hidden_messages,
        'members': members,
        'members_count': members_count,
        'pending_requests': pending_requests,
        'suspended_members': suspended_members
    }
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def join_room(request, pk):
    room = get_object_or_404(Room, id=pk)
    if request.user in room.members.all() or request.user in room.pending_requests.all():
        return redirect('home')

    if not room.open_status:
        room.pending_requests.add(request.user)
        return redirect('home')

    room.members.add(request.user)
    return redirect('room', pk=room.id)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render('delete-room', 'base/delete_room.html', {'obj': room})

@login_required(login_url='login')
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()

    context = {'user': user, 'rooms': rooms}

    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def message(request, pk):
    message = get_object_or_404(Message, id=pk)

    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = request.user
                comment.message = message
                comment.save()
        elif 'like_submit' in request.POST:
            if request.user in message.likes.all():
                message.likes.remove(request.user)
            else:
                message.likes.add(request.user)
            message.save()
        elif 'hide_submit' in request.POST:
                message.hidden_status = not message.hidden_status
                message.save()
        return redirect('room', pk=message.room.id)
    else:
        comment_form = CommentForm()

    likes_count = message.likes.count()
    comments = message.comment_set.all()
    comments_count = comments.count()

    context = {
        'message': message,
        'likes_count': likes_count,
        'comments': comments,
        'comments_count': comments_count,
        'comment_form': comment_form
    }
    return render(request, 'base/message.html', context)

@login_required(login_url='login')
def create_message(request, pk):
    pass




