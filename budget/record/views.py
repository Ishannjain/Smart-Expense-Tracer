from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse

from .models import *


def index(request):
    return render(request, "record/index.html")

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
    expense=Expense.objects.filter(user=request.user).select_related('category')
    return render(request,'record/display_expense.html',{
        "expenses":expense
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

