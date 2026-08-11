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
from datetime import date # for the foodlog



### PAGES ##########
"""
Function Name: loginPage, regPage, base, home, about, fitnessSurveyPage
Programmer: Jerry Ochoa

Displays the corresponding page when the user navigates to the URL. It renders the HTML 
template for each page and passes any necessary context data to the template.
"""
def login_register(request):
    return render(request, "login_register.html")

def dashboard(request):
    return render(request, "dashboard_v2.html")

def startup(request):
    return render(request, "startup.html")

def waterPage(request):
    return render(request, 'waterlog.html')

def fitness_survey(request):
    return render(request, "fitness_survey_v2.html")

def foodlogPage(request):
    userInfo = User.objects.get(id=request.session['userid'])
    profileInfo = Profile.objects.get(user=userInfo)
    todaysDate = date.today()

    #Target calories
    TC = TargetCalories.objects.get(profile=profileInfo)

    # Food log items
    foodlog = FoodLog.objects.filter(
        profile=profileInfo, 
        date=todaysDate
    ).first()
    entries = foodlog.foods.all()

    foodlog_cal = foodlog.calculateTotalCalories()

    return render(request, "foodlog.html", 
                  {
                    "entries": entries, 
                    "foodlog_cal": foodlog_cal,
                    "targetCalories": TC.target_calories
                    })


## Base(Home) is the main page to the website- able to toggle through pages
def base(request): 
    """
        Function Name: base
        Programmer: Jerry Ochoa

        The main goal of this function is to render the base.html to the page. Before we render 
        the page are also making checks such as whether or not a User is currently logged in. 
        If not, the page will redirect to the login page. We are also checking to see if the user 
        has completed their profile yet witch is the fitness survey. If no profile object has been
        created, then we set the profile field as None. This changes the contents of the frontend to 
        have the user fill out the fitness survey before accessing the other functionality of the page. 
    """
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
    # the Search is = Amount + Food
    if not request.POST['food']:
        return render(request, "foodlog.html", {"error": "Food Name can not be empty."})
    else:
        food = request.POST['food']

    if not request.POST['amount']:
        amount = "1"
    else:
        amount = request.POST['amount']

    # food = request.POST['food']
    # amount = request.POST['amount']
        
    search = amount +" "+ food

    # api_key = settings.calorieninjas_APIKey
    api_key = "x/emm0VcKlOoc+mRMURCIA==AzrAJ19yrPQ2s7eX"

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
    if len(data["items"]) == 0:
        foodInfo = {"name":"No Food item found. please search for another food"}
    else:    
        foodInfo = {
            "name": data["items"][0]["name"], #str, 
            "calories": data["items"][0]["calories"], #int
            "protein":data["items"][0]["protein_g"], #int,
            "carbs":data["items"][0]["carbohydrates_total_g"], #int
            "fiber":data["items"][0]["fiber_g"], #int
            "fat":data["items"][0]["fat_total_g"], #int
        }

    # ! once page is avalable update
    return render(request,'foodlog.html', {"foodInfo": foodInfo}) 
    
    
def addTo_Foodlog(request):
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
    foodObj = Food.objects.create(
        name = request.POST["name"], #str
        calories = float(request.POST["calories"]), #int
        protein = float(request.POST["protein"]), #int
        carbs = float(request.POST["carbs"]), #int
        fiber = float(request.POST["fiber"]), #int
        fat = float(request.POST["fat"]), #int
    )

    print("-"*20)
    print("***Food object***")
    print(foodObj)
    print("-"*20)

    # Checks to see if there is a food Log
    userInfo = User.objects.get(id=request.session['userid'])
    profileInfo = Profile.objects.get(user=userInfo)
    todaysDate = date.today() 

    foodlog_Check = FoodLog.objects.filter(profile=profileInfo, date=todaysDate).exists()

    # No foodLog - create one (profile, Date) -> createFoodlog()
    if foodlog_Check==False:
        foodlog = FoodLog.objects.create(
            profile = profileInfo,
            date = todaysDate,
        )
        foodlog.foods.add(foodObj)

    # food log found - update it
    else:
        foodlog = FoodLog.objects.get(profile=profileInfo, date=todaysDate)
        foodlog.foods.add(foodObj)
    return redirect('/food_log')


def removeFood(request):
    food = Food.objects.get(id=request.POST["food_id"])
    food.delete()
    return redirect("/food_log")


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
    userinfo = User.objects.get(id = user_id)

    # format the height
    height = request.POST['height']
    splitStr = height.split('.')
    feet = int(splitStr[0])
    inches = int(splitStr[1])
    height_inch = feet + inches 

    profile_Check = Profile.objects.filter(user=userinfo).exists()

    if profile_Check == True:
        # Updates the profile
        profile = Profile.objects.get(user=userinfo)
        profile.weight = int(request.POST['current_weight'])
        profile.height = height_inch
        profile.age = int(request.POST['age'])
        profile.sex = request.POST['sex']
        profile.activityLevels = request.POST['activity_level']
        profile.fitnessGoals = request.POST['fitness_goal']

    else:
        # creates the profile
        profile = Profile.objects.create(
            user = userinfo,
            weight = int(request.POST['weight']),
            height = height_inch,
            age = int(request.POST['age']),
            sex = request.POST['sex'],
            activityLevels = request.POST['activityLevels'],
            fitnessGoals = request.POST['fitnessGoals'],
        )

    # print("-"*20)
    # print("NEW PROFILE CREATED:")
    # print(profile)
    # print("-"*20)

    targCal_Check = TargetCalories.objects.filter(profile=profile).exists()

    if targCal_Check == True:
        # update TC
        targCal = TargetCalories.objects.get(profile=profile)
        targCal.target_calories = calculateTargetCalories(profile)
    else:
        # create the TC model
        targCal = TargetCalories.objects.create(
            profile=profile,
            target_calories = calculateTargetCalories(profile)
        )

    # print("-"*20)
    # print("TARGET CALORIES:")
    # print(targCal.target_calories)
    # print("-"*20)

    ## after creating profile object store Target calories
    # calculateTargetCalories(profile)


    return redirect('/dashboard')

# function that calculates target calories 
def calculateTargetCalories(profile):
    
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
    
