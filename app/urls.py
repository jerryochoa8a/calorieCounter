from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.loginPage, name='loginPage'), ##website opens to the login page
    path('regPage', views.regPage, name='regPage'),
    path('base', views.base, name="base"), 
    path('home', views.home, name='home'), 
    path('about', views.about, name='about'), 

    # Functions
    path('new_user', views.new_user), ## registers User
    path('user_login', views.user_login), ## Login User
    path('home/logout', views.logout), ##logout User    

]

