from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/send/<int:room_id>/', views.send_message, name='send_message'),
    path('chat/start/<int:user_id>/', views.start_private_chat, name='start_chat'),
]
