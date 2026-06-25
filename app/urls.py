from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginPage, name='loginPage'),

    path('new_user', views.new_user), #change function name
    path('user_login', views.user_login), # change function name
    path('success', views.success), #change function name
    path('success/logout', views.logout), # change function name

]

