from . import views
from django.urls import path


urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),

    path('room/<str:pk>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create-room'),
    path('delete-room/<str:pk>/', views.delete_room, name='delete-room'),
    path('join-room/<str:pk>/', views.join_room, name='join-room'),

    path('view-message/<str:pk>/', views.message, name='view-message'),
    path('create-message/<str:pk>/', views.create_message, name='create-message'),


    path('user-profile/<str:pk>/', views.user_profile, name='user-profile')
]
