"""
Name: urls.py
Date: 7/30/2026
Programmers: Jerry Ochoa and Jared Jasso

This module contains the url calls for the calorie counter app. These url calls are made through the
client side of the aplication and point to specific funtion in our views.py file. These calls are 
primarily made when submiting a form or redirecting to another page. The code below is seperated by
calls to render a page or calls to run a function action.  

"""
from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.loginPage, name='loginPage'), ##website opens to the login page
    path('regPage', views.regPage, name='regPage'),
    path('base', views.base, name="base"), 
    path('home', views.home, name='home'), 
    path('about', views.about, name='about'), 
    path('fitnessSurveyPage/', views.fitnessSurveyPage, name='fitnessSurveyPage'),

    # Functions
    path('new_user', views.new_user), ## registers User
    path('user_login', views.user_login), ## Login User
    path('logout', views.logout), ##logout User    
    path('fitnessSurvey', views.fitnessSurvey), ## submit Fitness Survey    

]

