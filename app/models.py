"""
Name: models.py
Date: 7/30/2026
Programmers: Jared Jasso and Jerry Ochoa

This module contains the models for our calorie counter app. The models represent the apps data which include 
users, profiles, target calories, food logs, food, and food log entries. We use these models to store, retrieve,
and manage the data for this app. 

"""

from django.db import models

# Create your models here.

class User(models.Model):
     """
     Class Name: User
     Programmer: Jerry Ochoa

     Stores the users information such as first name, last name, email, and password. It also records the date and 
     time when the user was created and last updated.

     """
     first_name = models.CharField(max_length=20)
     last_name = models.CharField(max_length=20)
     email = models.CharField(max_length=40)
     password = models.CharField(max_length=50)
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)

class Profile(models.Model):
     """
     Class Name: Profile
     Programmer: Jared Jasso

     It has a one-to-one relationship with the User model, meaning each user can have only one profile
     and if the user is deleted, the profile will also be deleted.

     Stores more detailed information about the user such as weight, height, age, sex, activity levels, and 
     fitness goals.

     """

     user = models.OneToOneField(User, on_delete=models.CASCADE)
     weight = models.IntegerField()
     height = models.IntegerField()
     age = models.IntegerField()

     sexChoices = [
        ("Male", "Male"),
        ("Female", "Female"),
     ]

     sex = models.CharField(
        max_length = 6,
        choices = sexChoices
     )


     activityLevelChoices = [
        ("Sedentary", "Sedentary"),
        ("Lightly Active", "Lightly Active"),
        ("Moderately Active", "Moderately Active"),
        ("Very Active", "Very Active"),
     ]

     activityLevels = models.CharField(
        max_length = 20,
        choices = activityLevelChoices
     )


     fitnessGoalChoices = [
        ("Lose Weight", "Lose Weight"),
        ("Maintain Weight", "Maintain Weight"),
        ("Gain Weight", "Gain Weight"),
     ]

     fitnessGoals = models.CharField(
        max_length = 20,
        choices = fitnessGoalChoices
     )

class TargetCalories(models.Model):
     """
     Class Name: TargetCalories
     Programmer: Jared Jasso

     It has a one-to-one relationship with the Profile model, meaning each profile can 
     have only have one target calories at a time. 
     
     Stores the target calories for a user based on their profile information. It also 
     records the date and time when the target calories were created and last updated.

     """

     profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

     target_calories = models.IntegerField()

     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)

class Food(models.Model):
     """
     Class Name: Food
     Programmer: Jared Jasso

     Stores information about food items such as name, calories, protein, carbs, and fat. 
     This will get information from api "calorieninjas" 

     The "__str__" method returns a readable string.

     """

     name = models.CharField(max_length=100)

     calories = models.IntegerField()
     protein = models.FloatField()
     carbs = models.FloatField()
     fat = models.FloatField()

     def __str__(self):
        return self.name


class FoodLog(models.Model):
     """
     Class Name: FoodLog
     Programmer: Jared Jasso

     Represents a food log for a user of a specific date. It uses a one to many relationship with profile. 
     It also stores the date of the log, and maintains a many-to-many relationship with the Food model 
     through the FoodLogEntry model. 

     The "calculateTotalCalories" method calculates the total calories consumed in the food log using 
     the FoodLogEntry model.

     The "__str__" method returns a readable string of user name and date of foodlog.

     """

     profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

     date = models.DateField()

     foods = models.ManyToManyField(Food, through="FoodLogEntry")

     def calculateTotalCalories(self):
        totalCalories = 0

        for entry in self.foodlogentry_set.all():
            totalCalories += entry.calculateCalories()

            return totalCalories

     def __str__(self):
         return (
            f"{self.profile.user.first_name}'s "
            f"Food log - {self.date}"
        )

class FoodLogEntry(models.Model):
     """
     Class Name: FoodLogEntry
     Programmer: Jared Jasso

     Represents a single food item that has been entered into a food log. 

     It has a many to one relationship with the FoodLog model and the Food model.
     If the food log or food item is deleted, the corresponding food log entry will also be deleted.

     The float field represents the quantity of the food item consumed.

     The "calculateCalories" method calculates the total calories for the food item 
     based on its quantity.

     The "__str__" method returns a readable string of the food name and quantity.

     """

     foodLog = models.ForeignKey(FoodLog, on_delete=models.CASCADE)

     food = models.ForeignKey(Food, on_delete=models.CASCADE)

     quantity = models.FloatField(default=1)   

     def calculateCalories(self):
        return self.food.calories * self.quantity

     def __str__(self):
        return (
            f"{self.food.name} - "
            f"{self.quantity} serving(s)"
            )
