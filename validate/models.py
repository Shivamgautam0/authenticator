from django.db import models


class users(models.Model):
    username = models.CharField(max_length=50)
    useremail = models.EmailField(unique= True, max_length=50)
    password = models.CharField(max_length=16)
    
    def __str__(self):
        return self.useremail