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
class Following(models.Model):
    follower=models.ForeignKey(User,related_name="following",on_delete=models.CASCADE)
    followed=models.ForeignKey(User,related_name="follower",on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"

class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"
class Profile(models.Model):
    user=models.ForeignKey(User,related_name="user",on_delete=models.CASCADE)
    imagurl=models.CharField(max_length=1000)
    About=models.CharField(max_length=1000)

class GroupExpense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_expenses')
    participants = models.ManyToManyField(User, related_name='group_expenses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

class Balance(models.Model):
    owed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owed_balances')
    owed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owing_balances')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('owed_by', 'owed_to')

    def __str__(self):
        return f"{self.owed_by} owes {self.owed_to} {self.amount}"
