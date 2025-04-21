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


def index(request):
    user = request.user
    today = timezone.now().date()

    # Filter income and expenses
    all_incomes = Income.objects.filter(user=user)
    all_expenses = Expense.objects.filter(user=user)

    # Calculate overall
    total_income = all_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = all_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Monthly (current month)
    monthly_incomes = all_incomes.filter(date__month=today.month, date__year=today.year)
    monthly_expenses = all_expenses.filter(date__month=today.month, date__year=today.year)
    monthly_income = monthly_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expense = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Yearly (current year)
    yearly_incomes = all_incomes.filter(date__year=today.year)
    yearly_expenses = all_expenses.filter(date__year=today.year)
    yearly_income = yearly_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    yearly_expense = yearly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,

        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,

        "yearly_income": yearly_income,
        "yearly_expense": yearly_expense,
    }
    return render(request, "record/index.html", context)




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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "record/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "record/login.html")
    
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
def profile(request,username):
    user=get_object_or_404(User,username=username)
    return render(request,'record/profile.html',{
        "user":user
    })

def profile_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        profile = request.user.profile
        profile.image.save(image.name, image)
        profile.save()
        return redirect('profile', username=request.user.username)

    return render(request, 'record/profile_view.html')

def add_friend(request,user_id):
     friend=User.objects.get(id=user_id)
     Friend.objects.create(
         current_user=request.user,
         friend=friend
     )
     return redirect('profile',username=friend.username)