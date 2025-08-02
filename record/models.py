from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import random
import string

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    imagurl = models.CharField(max_length=1000, blank=True)
    About = models.CharField(max_length=1000, blank=True)



class SplitRoom(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=8, unique=True, blank=True)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Edit/Delete after completion

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not SplitRoom.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return f"{self.name} ({self.code})"


class RoomMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(SplitRoom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user.username} in {self.room.name}"


class GroupExpense(models.Model):
    room = models.ForeignKey(SplitRoom, on_delete=models.CASCADE, related_name='group_expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_paid_expenses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount} in {self.room.name}"


class GroupExpenseShare(models.Model):
    expense = models.ForeignKey(GroupExpense, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    share_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} owes {self.share_amount} for {self.expense.description}"


class GroupDebt(models.Model):
    room = models.ForeignKey(SplitRoom, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_debts_owed')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_debts_to_collect')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('room', 'from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} owes {self.to_user.username}: {self.amount}"
