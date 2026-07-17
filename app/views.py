from django.shortcuts import render, redirect
from app.models import User
from django.contrib import messages
from django.http import HttpResponse
import bcrypt
from django.conf import settings
import requests
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


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

        # email errors:
        email = request.POST['email']

        # validates correct email format
        try:
            validate_email(email)
        except ValidationError:
            return render(request, "regPage.html", {"error": "Please enter a valid email address."})

        # validates if email is already in use
        if User.objects.filter(email=email).exists():
            return render(request, "regPage.html", {"error": "Email is already in use."})

        # first name errors:
        first_name = request.POST['fname']

        # first name is not empty
        if not first_name:
            return render(request, "regPage.html", {"error": "First name cannot be empty."})

        # last name errors:
        last_name = request.POST['lname']

        # last name is not empty
        if not last_name:
            return render(request, "regPage.html", {"error": "Last name cannot be empty."})

        # password errors:
        password = request.POST['password']

        # password is not empty
        if not password:
            return render(request, "regPage.html", {"error": "Password cannot be empty."})

        # password must be at least 8 characters long
        if len(password) < 8:
            return render(request, "regPage.html", {"error": "Password must be at least 8 characters long."})

        # hash the password
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # creates the user in the database
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


#food API search
def GetfoodInfo(search):
    # Search = Amount + Food
    api_key = settings.calorieninjas_APIKey

    url = "https://api.calorieninjas.com/v1/nutrition"
    headers = {
        "X-Api-Key": f"{api_key}"
    }
    params = {
        "query": f"{search}",
        #Ex) "query": "1 eggs",
    }
    response = requests.get(url,headers=headers, params=params)
    data = response.json()

    #Just display to the page to alow the use to confirm info -> addTo_foodlog()
    name =data["items"][0]["name"] #str
    calories =data["items"][0]["calories"] #int
    protein = data["items"][0]["protein_g"] #int
    carbs =data["items"][0]["carbohydrates_total_g"] #int
    fiber =data["items"][0]["fiber_g"] #int
    fat =data["items"][0]["fat_total_g"] #int
    
    
    
def addTo_Foodlog(foodInfo):
    #making the food object
    foodItem = Food.objects.create(
        name =foodInfo.name, #str
        calories = foodInfo.calories, #int
        protein = foodInfo.protein, #int
        carbs = foodInfo.carbs, #int
        fiber = foodInfo.fiber, #int
        fat = foodInfo.fat, #int
    )
    # get the food log with the the users ID and todays date
    foodLog = FoodLog.objects.filter(userID=request.POST[''], date="todays date" )
    # [if] there is no foodLog found then make one(userID, Date) -> createFoodlog()

    foodLog.log = foodItem_id


# def createFoodlog(userID, Date):
#     Foodlog.objects.create(
#         log = [],
#         user_id = userid,
#         date = todays date,
#     )

