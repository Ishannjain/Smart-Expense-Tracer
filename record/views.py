from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Sum
from decimal import Decimal
from django.db.models import Q
from .models import *
from datetime import datetime
from django.core.paginator import Paginator
from datetime import date
from django.utils import timezone 

from datetime import timedelta



from django.contrib.auth.decorators import login_required
import os
from django.contrib import messages

def check(password):
    if len(password) < 8:
        return False
    isUpper = False
    isLower = False
    isDigit = False
    for ch in password:
        if ch.isupper():
            isUpper = True
        if ch.islower():
            isLower = True
        if ch.isdigit():
            isDigit = True
    
    return isUpper and isLower and isDigit
@login_required
def index(request):
    now = timezone.now()

    # User's income, expense, and budget queries
    total_income = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense

    # Monthly data
    monthly_income = Income.objects.filter(user=request.user, date__month=now.month).aggregate(total=Sum('amount'))['total'] or 0
    monthly_expense = Expense.objects.filter(user=request.user, date__month=now.month).aggregate(total=Sum('amount'))['total'] or 0
    monthly_budget = Budget.objects.filter(user=request.user, period='monthly').first().amount if Budget.objects.filter(user=request.user, period='monthly').exists() else 0

    # Yearly data
    yearly_income = Income.objects.filter(user=request.user, date__year=now.year).aggregate(total=Sum('amount'))['total'] or 0
    yearly_expense = Expense.objects.filter(user=request.user, date__year=now.year).aggregate(total=Sum('amount'))['total'] or 0

    # Render the dashboard
    return render(request, 'record/index.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_budget': monthly_budget,
        'yearly_income': yearly_income,
        'yearly_expense': yearly_expense,
        'now': now
    })




def categories_list(request):
    if request.method=='POST':
        name=request.POST.get('name')
        if name:
            Category.objects.create(
                name=name,
                user=request.user
                )
            return redirect('categories_list')
    categories=Category.objects.filter(user=request.user)
    return render(request,'record/categories_list.html',{
        "categories":categories
    })
def add_income(request):
   
    if request.method=='POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        note = request.POST.get('note')
        Income.objects.create(
            user=request.user,
            amount=amount,
            date=date,
            note=note
        )
        return redirect('display_income')
    return render(request,'record/add_income.html')
def display_income(request):
    income_list=Income.objects.all()
    paginator=Paginator(income_list,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    income=Income.objects.filter(user=request.user)
    total_income = income.aggregate(total=Sum('amount'))['total'] or 0
    income = income.order_by('-date') 
    return render(request,'record/display_income.html',{
        "incomes":income,
        "total_income":total_income,
        "page_obj":page_obj
    })
def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', '')
            if next_url:
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "record/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "record/login.html", {
            "next": request.GET.get('next', '')
        })
    
    
def display_expense(request):
    query = request.GET.get('q')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    tags = request.GET.get('tags', '')
    expense_list=Expense.objects.all()
    paginator=Paginator(expense_list,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    income=Income.objects.filter(user=request.user)
    expenses = Expense.objects.select_related('category').filter(user=request.user)
    if query:
        expenses = expenses.filter(
            Q(note__icontains=query) |
            Q(category__name__icontains=query)
        )

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            expenses = expenses.filter(date__range=(start, end))
        except ValueError:
            pass  # Handle invalid date formats if necessary

    

    expenses = expenses.order_by('-date') 
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    return render(request,'record/display_expense.html',{
        "expenses":expenses,
        "total_expense":total_expense,
        "page_obj":page_obj
    })
def add_expense(request):
    categories=Category.objects.filter(user=request.user)
    if request.method=='POST':
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        note = request.POST.get('note')
        category = Category.objects.get(id=category_id, user=request.user)
        Expense.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            date=date,
            note=note
        )
        return redirect('display_expense')
    return render(request,'record/add_expense.html',{
        "categories":categories
    })
def edit_expense(request,expense_id):
    expense=get_object_or_404(Expense,id=expense_id,user=request.user)
    categories=Category.objects.filter(user=request.user)
    if request.method=="POST":
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        note = request.POST.get('note')
        if not amount or not category_id or not date:
            return render(request,'record/edit_expense.html',{
                "categories":categories,
                "expense":expense,
                "message":'please fill all requirements'
            })
        try:
            category=Category.objects.get(id=category_id,user=request.user)
        except Category.DoesNotExist:
             return render(request,'record/edit_expense.html',{
                "categories":categories,
                "expense":expense,
                "message":'invalid Category'
            })
        expense.amount=amount
        expense.date=date
        expense.category=category
        expense.note=note
        expense.save()
        return redirect('display_expense')
    return render(request,'record/edit_expense.html',{
                "categories":categories,
                "expense":expense
            })
def delete_expense(request,expense_id):
    expense=get_object_or_404(Expense,id=expense_id,user=request.user)
    expense.delete()
    return redirect('display_expense')
def edit_income(request,income_id):
    income=get_object_or_404(Income,id=income_id,user=request.user)
    if request.method=="POST":
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        note = request.POST.get('note')
        if not amount or not date:
            return render(request,'record/edit_income.html',{
            
                "income":income,
                "message":'please fill all requirements'
            })
        
        income.amount=amount
        income.date=date
        
        income.note=note
        income.save()
        return redirect('display_income')
    return render(request,'record/edit_income.html',{
                
                "income":income
            })

def delete_income(request,income_id):
    income=get_object_or_404(Income,id=income_id,user=request.user)
    income.delete()
    return redirect('display_income')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not check(password):
                    return render(request, "auction/register.html", {
                        "message": "Passwords does not meet requirements. Minimun length 8 and should contain atleast one Capital Letter, one small Letter and one digit"
                    })

        if password != confirmation:
            return render(request, "record/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "record/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "record/register.html")

def create_budget(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')

        # Validate and process the data
        try:
            category = Category.objects.get(id=category_id, user=request.user)
            amount = float(amount)
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

            # Create and save the budget
            Budget.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                period=period,
                start_date=start_date
            )
            return redirect('display_budget')
        except (Category.DoesNotExist, ValueError):
            # Handle errors (e.g., invalid input)
            pass

    # For GET request, render the form
    categories = Category.objects.filter(user=request.user)
    return render(request, 'record/create_budget.html', {
        'categories': categories
        })


def display_budget(request):
    budget_list=Budget.objects.all()
    paginator=Paginator(budget_list,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    income=Income.objects.filter(user=request.user)
    query = request.GET.get('q')
    budgets = Budget.objects.filter(user=request.user)
    budget_data = []
    expenses = Expense.objects.select_related('category').filter(user=request.user)
    if query:
        expenses = expenses.filter(
            Q(note__icontains=query) |
            Q(category__name__icontains=query)
        )
        
    for budget in budgets:
        expenses = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            date__gte=budget.start_date
        )
        total_spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        remaining = budget.amount - total_spent

        # Ensure that 25% calculation uses Decimal instead of float
        warning_level = None
        if remaining <= Decimal('0.00'):
            warning_level = 'exhausted'
        elif remaining <= budget.amount * Decimal('0.25'):
            warning_level = 'low'

        budget_data.append({
            'budget': budget,
            'expenses': expenses,
            'total_spent': total_spent,
            'remaining': remaining,
            'warning_level': warning_level
        })

    return render(request, 'record/display_budget.html', {
        'budget_data': budget_data,
        "page_obj":page_obj
        })
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        category_id = request.POST.get('category')

        # Validate inputs
        if not all([amount, period, start_date, category_id]):
            return render(request, 'record/edit_budget.html', {
                'budget': budget,
                'categories': categories,
                'message': 'All fields are required.'
            })

        try:
            category = Category.objects.get(id=category_id, user=request.user)
            budget.amount = float(amount)
            budget.period = period
            budget.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            budget.category = category
            budget.save()
            return redirect('display_budget')
        except (Category.DoesNotExist, ValueError):
            return render(request, 'record/edit_budget.html', {
                'budget': budget,
                'categories': categories,
                'message': 'Invalid data provided.'
            })

    return render(request, 'record/edit_budget.html', {
        'budget': budget,
        'categories': categories
    })
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    if request.method == 'POST':
        budget.delete()
        return redirect('display_budget')
    return render(request, 'record/delete_budget.html', {'budget': budget})

@login_required
def find_users(request):
    query = request.GET.get('q', '')
    results = User.objects.filter(username__icontains=query).exclude(id=request.user.id) if query else []
    connections = Following.objects.filter(follower=request.user).values_list('followed_id', flat=True)

    return render(request, 'record/find_users.html', {
        'query': query,
        'results': results,
        'connections': connections
    })
@login_required
def toggle_follow(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if request.user == target_user:
        return redirect('profile_view', user_id=target_user.id)  # Don't follow yourself

    if request.method == 'POST':
        existing = Following.objects.filter(follower=request.user, followed=target_user)
        if existing.exists():
            existing.delete()
        else:
            Following.objects.create(follower=request.user, followed=target_user)

    return redirect('profile_view', user_id=target_user.id)
@login_required
def profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    # Get actual user objects
    follower_links = Following.objects.filter(followed=profile_user)
    followers = [link.follower for link in follower_links]

    following_links = Following.objects.filter(follower=profile_user)
    following = [link.followed for link in following_links]

    is_following = Following.objects.filter(follower=request.user, followed=profile_user).exists()

    return render(request, 'record/profile.html', {
        'profile_user': profile_user,
        'followers': followers,
        'following': following,
        'is_following': is_following
    })
@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
# prevent chat with yourself
    if other_user == request.user:
        return redirect('profile_view', user_id=request.user.id)  # Or maybe show a message
#  handle message sending
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Chat.objects.create(sender=request.user, receiver=other_user, message=message)
#  retrieve all old chats with timestamps
    messages = Chat.objects.filter(
        models.Q(sender=request.user, receiver=other_user) |
        models.Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    return render(request, 'record/chat.html', {
        'other_user': other_user,
        'messages': messages
    })
# views.py
from django.core.files.storage import FileSystemStorage

@login_required
def edit_profile(request, user_id):
    # Get the user whose profile we want to edit
    profile_user = get_object_or_404(User, id=user_id)
    
    # Ensure only the profile owner can edit their profile
    if request.user != profile_user:
        return HttpResponseRedirect(reverse('profile_view', args=[user_id]))

    # Try to get the Profile, if it doesn't exist, create a new one
    profile, created = Profile.objects.get_or_create(user=profile_user)

    if request.method == 'POST':
        about = request.POST.get('about')
        image = request.FILES.get('imagurl')

        if about:
            profile.About = about

        if image:
            # Delete old image if exists
            if profile.imagurl:
                try:
                    os.remove(profile.imagurl.path)
                except:
                    pass
            
            # Save new image
            profile.imagurl = image

        try:
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view', user_id=user_id)
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    return render(request, 'record/edit_profile.html', {
        'profile': profile
    })

