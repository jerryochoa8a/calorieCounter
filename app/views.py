from django.shortcuts import render, redirect
from app.models import User
from django.contrib import messages
from django.http import HttpResponse
import bcrypt

### PAGES ##########

def loginPage(request):
    return render(request, "loginPage.html")

def regPage(request):
    return render(request, "regPage.html")

def home(request):
    if request.session.get('userid'):
        messages.error(request, "Successfully logged in!")
        return render(
            request,
            'home.html',
            {"user" : User.objects.get(id=request.session['userid'])}
        )

    return redirect('/')


#########################################


# Creating a new user
def new_user(request):
        # If errors: re-render page with error
        # else:
        password = request.POST['password']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        User.objects.create(
            first_name = request.POST['fname'],
            last_name = request.POST['lname'],
            email = request.POST['email'],
            password = pw_hash
        )
        print(User.objects.all())

        return redirect('/')


# Logging in an existing user
def user_login(request):
    user = User.objects.filter(email=request.POST['login_email'])
    if user:
        logged_user = user[0]
        if bcrypt.checkpw(request.POST['login_pw'].encode(), logged_user.password.encode()):
            request.session['userid'] = logged_user.id # Home function
            return redirect('/home')
    else:
        messages.error(request, "Wrong email or password")
        return redirect('/') # This will redirect to home page if the user login failed 


# Logging out a user
def logout(request):
    request.session.pop('userid', None) # Takes the user out of the session
    messages.error(request, "You have successfully logged out!")
    return redirect('/')


 

