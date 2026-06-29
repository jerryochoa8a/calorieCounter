from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.loginPage, name='loginPage'),
    path('regPage', views.regPage, name='regPage'),
    path('home', views.home),

    # Functions
    path('new_user', views.new_user), 
    path('user_login', views.user_login),
    path('home/logout', views.logout), 
    

]

