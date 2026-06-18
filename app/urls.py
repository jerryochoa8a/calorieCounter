from django.urls import path
from . import views

urlpattherns = [
    path('', views.home, name='home'),

]