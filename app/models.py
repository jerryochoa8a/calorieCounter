from django.db import models

# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.CharField(max_length=40)
    # weight = models.IntegerField()
    # height = models.IntegerField()
    # age = models.IntegerField()
    # gender = models.CharField()
    password = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Jerry -  Note you might need to change the varable names before you migrate !!!