# validate/models.py
from django.db import models
from django.contrib.auth.models import User

# We'll use Django's built-in User model
# This profile model can be used to store additional user information if needed
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.email