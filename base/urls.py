from . import views
from django.urls import path


urlpatterns = [
    path('', views.home, name='home'),

    path('create-room/', views.create_room, name='create-room'),
    path('delete-room/<str:pk>/', views.delete_room, name='delete-room'),

    path('create-message/<str:pk>/', views.create_message, name='create-message'),
    path('create-comment/<str:pk>/', views.create_comment, name='create-comment')
]