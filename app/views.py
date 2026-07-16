from django.shortcuts import render, redirect
from app.models import User
from django.contrib import messages
from django.http import HttpResponse
import bcrypt
import requests

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
    else:
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
        # print(User.objects.all())

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


def getFoodCalories(request): # Search = Amount + Food
    search = request.POST['amount'] + request.POST['food']

    url = "https://api.calorieninjas.com/v1/nutrition"
    headers = {
        "X-Api-Key": "x/emm0VcKlOoc+mRMURCIA==AzrAJ19yrPQ2s7eX"
    }
    params = {
        "query": f"{search}",
        # "query": "1 eggs",
    }
    response = requests.get(url,headers=headers, params=params)
    data = response.json()

    ## We can put this data in a object and to the page.
    ## we can have the user see and confirm the data then
    ## have another function save the confirmed data to user food log

    name = data["items"][0]["name"] #str
    calories = data["items"][0]["calories"] #int
    protein = data["items"][0]["protein_g"] #int
    carbs = data["items"][0]["carbohydrates_total_g"] #int
    fiber = data["items"][0]["fiber_g"] #int
    fat =  data["items"][0]["fat_total_g"] #int

def addToFoodlog(foodData):
    Food.objects.create( #Food model
        food = foodData.name,
        protein = foodData.protein,
        carbs = foodData.carbs,
        fiber = foodData.fiber,
        fat = foodData.fat
    )
    
    ## if food log at this date wasnt created at this date
    ## we should make one.
    ## maybe we can make the food long once we open the search page.
    ## the user doesnt have to add anything to there log but at least its 
    ## created

    # FoodLog.objects.create(
    #     userID = user id
    #     log = the Food ID
    #     date = todays date
    # )