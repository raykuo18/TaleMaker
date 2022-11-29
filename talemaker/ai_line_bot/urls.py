from django.urls import path
from . import views

views.ChatBot()
urlpatterns = [
    path('callback', views.ChatBot.callback)
]