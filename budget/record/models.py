from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    pass
class Category(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
class Expense(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    date=models.DateField()
    note=models.TextField(blank=True,max_length=1000)
    
class Income(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    note=models.TextField(blank=True,max_length=1000)
    date=models.DateField()
class Budget(models.Model):
    PERIOD_CHOICES=[
    ('montly','Monthly'),
    ('yearly','Yearly')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    start_date = models.DateField()
class Profile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='profile_images/',default='default.jpg')
    about=models.TextField(blank=True)
    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
class Friend(models.Model):
    current_user = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend', on_delete=models.CASCADE)