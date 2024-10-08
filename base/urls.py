from . import views
from django.urls import path


urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_page, name='login'),
    path('update-user', views.update_user, name='update-user'),
    path('register/', views.register_page, name='register'),

    path('room/<str:pk>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create-room'),
    path('update-room/str:pk/', views.update_room, name='update-room'),
    path('delete-room/<str:pk>/', views.delete_room, name='delete-room'),
    path('join-room/<str:pk>/', views.join_room, name='join-room'),

    path('message/<str:pk>/', views.message, name='message'),
    path('create-message/<str:pk>/', views.create_message, name='create-message'),

    path('create-poll/<str:pk>/', views.create_poll, name='create-poll'),
    path('poll/<str:pk>/', views.poll, name='poll'),
    path('create-choice/<str:pk>/', views.create_choice, name='create-choice'),

    path('event/<str:pk>/', views.event, name='event'),
    path('create-event/<str:pk>/', views.create_event, name='create-event'),
    path('user-profile/<str:pk>/', views.user_profile, name='user-profile')
]
