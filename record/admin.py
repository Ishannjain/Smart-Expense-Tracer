from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Budget)
admin.site.register(Following)
admin.site.register(Chat)
admin.site.register(Profile)
admin.site.register(SplitRoom)
admin.site.register(GroupDebt)
admin.site.register(GroupExpense)
admin.site.register(GroupExpenseShare)
admin.site.register(RoomMembership)

