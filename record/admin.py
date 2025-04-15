from django.contrib import admin
from .models import User,Category,Expense
# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Expense)