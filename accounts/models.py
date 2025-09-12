from django.db import models

# Create your models here.
class Admin(models.Model):
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) 

class Student(models.Model):
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)



from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=200)   # Event name
    date = models.DateField()                 # Event date
    participants_allowed = models.PositiveIntegerField()  # Number of participants
    venue = models.CharField(max_length=200)  # Venue

    created_at = models.DateTimeField(auto_now_add=True)  # When event was created
    updated_at = models.DateTimeField(auto_now=True)      # Last updated

    def __str__(self):
        return f"{self.name} ({self.date})"




