from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .forms import RoomForm, CommentForm, MessageForm, PollForm, EventForm
from .models import Room, Message, Comment, Event, Choice, Poll, Notification, AdminNotification

# Create your views here.

def save_notification(
                      room: Room,
                      action_by: User,
                      message: Message,
                      action_to: User,
                      action_type: str,
                      ) -> None:
    user_notification = Notification(
        action_by=action_by,
        action_to=action_to,
        room=room,
        message=message,
        action_type=action_type
    )
    admin_notification = AdminNotification(
        action_by=action_by,
        action_to=action_to,
        room=room,
        message=message,
        action_type=action_type
    )

    user_notification.save()
    admin_notification.save()

def home(request):
    my_rooms, admin_notifications, notifications = [], [], []

    if not request.user.is_authenticated:
        open_rooms = Room.objects.filter(open_status=True)
        closed_rooms = Room.objects.filter(open_status=False)
    else:
        if request.method == 'POST':
            if 'read-notification' in request.POST:
                notification = Notification.objects.get(id=request.POST.get('notification_id'))
                notification.read_status = True
                notification.save()
            elif 'read-admin-notification' in request.POST:
                admin_notification = AdminNotification.objects.get(id=request.POST.get('admin_notification_id'))
                admin_notification.read_status = True
                admin_notification.save()
            return redirect('home')
        my_rooms = Room.objects.filter(members=request.user)
        open_rooms = Room.objects.exclude(members=request.user).filter(open_status=True)
        closed_rooms = Room.objects.exclude(members=request.user).filter(open_status=False)
        notifications = Notification.objects.filter(action_to=request.user, read_status=False)
        admin_notifications = AdminNotification.objects.filter(room__admins=request.user, read_status=False)
    rooms_count = Room.objects.all().count()
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    search_rooms = Room.objects.filter(
        Q(title__icontains=q) |
        Q(description__icontains=q)
    )[0:5]
    context = {
        'my_rooms': my_rooms,
        'open_rooms': open_rooms,
        'closed_rooms': closed_rooms,
        'rooms_count': rooms_count,
        'search_rooms': search_rooms,
        'notifications': notifications,
        'admin_notifications': admin_notifications
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
def update_user(request):
    pass

@login_required(login_url='login')
def create_room(request):

    if request.method == 'POST':
        room_form = RoomForm(request.POST.get('room_form'))
        if room_form.is_valid():
            room = room_form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'room_form': Roomform()}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_poll(request, pk):
    pass

@login_required(login_url='login')
def update_room(request, pk):
    pass

@login_required(login_url='login')
def room(request, pk):
    room = get_object_or_404(Room, id=pk)

    if not request.user in room.members.all():
        return HttpResponse('You are not allowed here')

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
    room_events = room.event_set.all()
    room_polls = room.poll_set.all()

    context = {
        'room': room,
        'room_messages': room_messages,
        'hidden_messages': hidden_messages,
        'members': members,
        'members_count': members_count,
        'pending_requests': pending_requests,
        'suspended_members': suspended_members,
        'room_events': room_events,
        'room_polls': room_polls
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
                save_notification(
                    room=message.room,
                    action_by=request.user,
                    action_to=message.author,
                    message=message,
                    action_type='c'
                )
        elif 'like_submit' in request.POST:
            if request.user in message.likes.all():
                message.likes.remove(request.user)
            else:
                message.likes.add(request.user)
            message.save()
            save_notification(
                room=message.room,
                action_by=request.user,
                action_to=message.author,
                message=message,
                action_type='l'
            )
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
    room = get_object_or_404(Room, id=pk)

    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.room = room
            message.author = request.user
            message.save()

            return redirect('message', pk=message.id)
    else:
        message_form = MessageForm()
        context = {
            'message_form': message_form
        }
        return render(request, 'base/create_message.html', context)

@login_required(login_url='login')
def poll(request, pk):

    poll = get_object_or_404(Poll, id=pk)
    if not request.user in poll.room.members.all():
        return HttpResponse('You are not allowed here')
    else:
        if request.method == 'POST':
            if 'vote' in request.POST:
                if request.user in poll.voted_users.all():
                    return render(
                        request,
                        'base/poll.html',
                        {
                            'poll': poll,
                            'error_message': 'You already voted on this poll'
                        }
                    )

                try:
                    selected_choice = poll.choice_set.get(id=request.POST['choice'])

                except(KeyError, Choice.DoesNotExist):
                    return render(
                        request,
                        'base/poll.html',
                        {
                            'poll': poll,
                            'error_message': 'You did not select a choice'
                        }
                    )
                else:
                    selected_choice.votes = F('votes') + 1
                    selected_choice.save()
                    poll.voted_users.add(request.user)
                    poll.save()
                    return render(
                        request,
                        'base/poll.html',
                        {
                            'poll': poll,
                            'error_message': 'You already voted on this poll'
                        }
                    )
        context = {
                'poll': poll
            }
        return render(request, 'base/poll.html', context)

@login_required(login_url='login')
def create_poll(request, pk):
    poll_room = get_object_or_404(Room, id=pk)
    if not request.user in poll_room.admins.all():
        return HttpResponse('You are not allowed to make this request')

    if request.method == 'POST':
        poll_form = PollForm(request.POST.get('poll_form'))
        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.created_by = request.user
            poll.room = poll_room
            poll.save()
            return redirect('poll', pk=poll.id)
    else:
        poll_form = PollForm()
        context = {
            'poll_form': poll_form
        }
        return render(request, 'base/poll_form.html', context)
@login_required(login_url='login')
def event(request, pk):
    event = get_object_or_404(Event, id=pk)
    if not request.user in event.room.members.all():
        return HttpResponse('You are not allowed to make this request')

    if request.method == 'POST':
        if event.has_ended():
            return HttpResponse('Event has ended')
        if request.user in event.accepted_set.all() or request.user in event.rejected_set.all():
            return render(request, 'base/event.html', {
                'event': event,
                'error_message': 'You already accepted or rejected this event'
            })
        else:
            if 'accepted' in request.POST:
                #TODO: Send a notification to user
                event.accepted.add(request.user)
            elif 'rejected' in request.POST:
                #TODO: Do not send notification
                event.rejected.add(request.user)
            return redirect('event', event.id)
    else:
        context = {'event': event}
        return render(request, 'base/event.html', context)

@login_required(login_url='login')
def create_event(request, pk):
    event_room = get_object_or_404(Room, id=pk)
    if not request.user in event_room.admins.all():
        return HttpResponse('You are not allowed to make this request')

    if request.method == 'POST':
        event_form = EventForm(request.POST.get('event_form'))
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.created_by = request.user
            event.room = event_room
            event.save()

            return redirect('event', pk=event.id)
    else:
        event_form = EventForm()
        context = {
            'event_form': event_form
        }
        return render(request, 'base/event_form.html', context)
