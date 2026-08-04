"""
Module Name: views.py
Date: 7/30/2026
Programmers: Jerry Ochoa and Jared Jasso

This module contains the functions for the calorie counter app. It handles page navigation, 
user registration, login/logout, food searches using an external API, food log managenment
and target calorie calculations.   

"""
from django.shortcuts import render, redirect
from app.models import User, Profile, TargetCalories, FoodLog, Food
from django.contrib import messages
from django.http import HttpResponse
import bcrypt
from django.conf import settings
import requests
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



### PAGES ##########
"""
Function Name: loginPage, regPage, base, home, about, fitnessSurveyPage
Programmer: Jerry Ochoa

Displays the corresponding page when the user navigates to the URL. It renders the HTML 
template for each page and passes any necessary context data to the template.
"""
def loginPage(request):
    return render(request, "loginPage.html")


def regPage(request):
    return render(request, "regPage.html")


## Base(Home) is the main page to the website- able to toggle through pages
def base(request): 
    ##!!DOCUMENT!!##
    if request.session.get('userid'):
        userInfo = User.objects.get(id=request.session['userid'])

        # Checks to see if the user has created a Profile
        try:
            profileInfo = Profile.objects.get(user = userInfo)
        except Profile.DoesNotExist:
            profileInfo = None

        return render(
            request,
            'base.html',
            {"user" : userInfo, "profileInfo": profileInfo}
            
        )
    else:
        return redirect('/')


def fitnessSurveyPage(request):
    return render(request, "fitnessSurveyPage.html")


def foodLogPage(request):
    return(request, "foodLogPage.html")


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


#########################################

# Creating a new user
def new_user(request):

     """
     Function Name: new_user
     Programmer: Jared Jasso

     Handles the registration of a new user. It stores different error messages in case new user input is invalid.
     If new user input is valid, it creates a new user in the database with the first name, last name, email, and 
     hashed password. It then redirects the user to the base page after successful registration.
     """

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
    #  print(User.objects.all())

     return redirect('/base')


# Logging in an existing user
def user_login(request):

     """
     Function Name: user_login
     Programmer: Jared Jasso

     Function handles the login of an existing user. It checks if
     the submitted email matches an existing user, if it does 
     it checks if the submitted password matches the hashed 
     password stored in the database. If it does not, it shows an 
     error message, if it does it redirects the user to the base page
     and stores the user's ID in the session.

     """
     user = User.objects.filter(email=request.POST['login_email'])
     if user:
         logged_user = user[0]
         if bcrypt.checkpw(request.POST['login_pw'].encode(), logged_user.password.encode()):
             request.session['userid'] = logged_user.id
             return redirect('/base')
         else:
             errorMessage = {"error": "Wrong email or password"}
             return render(request,'loginPage.html', errorMessage) # This will redirect to home page if the user login failed 


# Logging out a user
def logout(request):

     """
     Function Name: logout
     Programmer: Jared Jasso
    
     Function handles the logout of a user. It removes the user's ID from the session and displays a message
     indicating that the user has successfully logged out. It then redirects the user to the login page.
    
     """

     request.session.pop('userid', None) # Takes the user out of the session
     messages.error(request, "You have successfully logged out!")
     return redirect('/')


# creating the user profile
def fitnessSurvey(request):
    """
    Function Name: fitnessSurvey
    Programmer: Jerry Ochoa
    
    This function handles the creation of the Profile Object for the user.
    We use the name "fitness survey" because best describes the type of information
    that we need to ultimately finalize the users profile. We first get the User 
    Object through the stored session id (current logged in user id). 
    With the User Object, we now create a one-to-one relationship when making 
    the users Profile by assigning the Object to the user field. We then transform
    weight, height, and age into intagers before passing them into their fields 
    because this information will later be used to calculate the users "Target Calories".
    """
    user_id = request.session.get('userid')
    user = User.objects.get(id = user_id)

    profile = Profile.objects.create(
        user = user,
        weight = int(request.POST['weight']),
        height = int(request.POST['height']),
        age = int(request.POST['age']),
        sex = request.POST['sex'],
        activityLevels = request.POST['activityLevels'],
        fitnessGoals = request.POST['fitnessGoals'],
    )

    ## after creating profile object store Target calories
    # calculateTargetCalories(profile.id)

    return redirect('/base')
    

#food API search
def GetfoodInfo(request):
    """
    Function Name: GetfoodInfo
    Programmer: Jerry Ochoa

    This function searches for food information using the CalorieNinjas API.
    The API works best when giving an amount, such as serving size, first then 
    the foods name. The search returns a JSON response where we then transform
    and extract the data into a dictionary.
    (Future Plans) - this information will pass the nutritional information to 
    a template for the user to confirm, before storing into the users food log. 
    """
    # Search = Amount + Food
    amount = request.POST['amount']
    food = request.POST['food']
    search = amount + food

    api_key = settings.calorieninjas_APIKey

    url = "https://api.calorieninjas.com/v1/nutrition"
    headers = {
        "X-Api-Key": f"{api_key}"
    }
    params = {
       #Ex) "query": "1 eggs",
       "query": f"{search}",
    }
    response = requests.get(url,headers=headers, params=params)
    data = response.json()

    #Just display to the page to alow the user to confirm info -> addTo_foodlog()    
    foodInfo = {
        "name": data["items"][0]["name"], #str, 
        "calories": data["items"][0]["calories"], #int
        "protein":data["items"][0]["protein_g"], #int,
        "carbs":data["items"][0]["carbohydrates_total_g"], #int
        "fiber":data["items"][0]["fiber_g"], #int
        "fat":data["items"][0]["fat_total_g"], #int
    }

    # ! once page is avalable update
    return render(request,'html', foodInfo) 
    
    
def addTo_Foodlog(request, foodInfo):
    """
    Function Name: addTo_Foodlog
    Programmer: Jerry Ochoa

    This function will run after the user has confirmed the food information.
    We first create a food object with the dictionary that came from our CalorieNinjas API.
    We then check to see if the users profile already has a food log for the current date.
    If it does not then we create one and add the food item. If it does then we get the
    food log and add the food item to the log.
    """
    # Makes the food Object - with dictionary
    foodItem = Food.objects.create(
        name =foodInfo.name, #str
        calories = foodInfo.calories, #int
        protein = foodInfo.protein, #int
        carbs = foodInfo.carbs, #int
        fiber = foodInfo.fiber, #int
        fat = foodInfo.fat, #int
    )

    # Checks to see if there is a food Log
    userInfo = User.objects.get(id=request.session['userid'])
    profileInfo = Profile.objects.get(user=userInfo) 

    foodlog_Check = FoodLog.objects.filter(profile=profileInfo, date=date).exists()

    # No foodLog - create one (profile, Date) -> createFoodlog()
    if foodlog_Check==False:
        FoodLog.objects.create(
            profile = profileInfo,
            # date = date,
            food=foodItem
        )
    # food log found - update it
    else:
        foodLog = FoodLog.objects.get(profile=profileInfo, date=date)
        foodLog.objects.update(
            food = foodItem
        )
    return()


# function that calculates target calories 
def calculateTargetCalories(request, profile_id):
    
    """
    Function Name: calculateTargetCalories
    Programmer: Jared Jasso

    Function calculates the target calories for a user based on their profile information.
    It calculates the Basal Metabolic Rate (BMR) based on the user's sex, weight, height,
    and age. It then applies an activity level multiplier based on the user's activity level.
    Finally, it adjusts the target calories based on the user's fitness goal (lose weight, 
    gain weight, or maintain weight). 

    The function uses the Mifflin-St Jeor equation to calculate BMR and returns the target calories as an integer.

    Female BMR = (10 * weight) + (6.25 * height) - (5 * age) - 161
    Male BMR = (10 * weight) + (6.25 * height) - (5 * age) + 5

    """

    profile = Profile.objects.get(id=profile_id)

    # calculates body mass rate (BMR) based on sex, weight, height, and age

    if profile.sex == "Female":
        BMR = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) - 161
    else:
        BMR = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) + 5

    # activity level multipliers

    if profile.activityLevels == "Sedentary":
        activityMultiplier = 1.2

    elif profile.activityLevels == "Lightly Active":
        activityMultiplier = 1.375

    elif profile.activityLevels == "Moderately Active":
        activityMultiplier = 1.55

    elif profile.activityLevels == "Very Active":
        activityMultiplier = 1.725

    # calculates target calories based on BMR, activity level, and fitness goal

    targetCalories = BMR * activityMultiplier

    # adjusts target calories based on fitness goal

    if profile.fitnessGoals == "Lose Weight":
        targetCalories -= 500

    elif profile.fitnessGoals == "Gain Weight":
        targetCalories += 500

    elif profile.fitnessGoals == "Maintain Weight":
        targetCalories = targetCalories

    return targetCalories
    
