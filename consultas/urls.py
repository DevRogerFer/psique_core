from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.consultas, name='consultas'),
    path('stream_response/<int:id>', views.stream_response, name='stream_response'),
    path('chat/<int:id>', views.chat, name='chat'),
    path('gravacao/<int:id>', views.gravacao, name='gravacao'),
]
