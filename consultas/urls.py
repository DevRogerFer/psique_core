from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.consultas, name='consultas'),
    path('stream_response/<int:id>', views.stream_response, name='stream_response'),
    path('chat/<int:id>', views.chat, name='chat'),
    path('gravacao/<int:id>', views.gravacao, name='gravacao'),
    path('ver_referencias/<int:id>', views.ver_referencias, name='ver_referencias'),
    path('send_message/<int:id>', views.send_message, name='send_message')
]
