from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("categories/",views.categories_list,name="categories_list"),
    path("add_expense/",views.add_expense,name="add_expense"),
    path("display_expense/",views.display_expense,name="display_expense"),
    path("edit_expense/<int:expense_id>/",views.edit_expense,name="edit_expense"),
    path("delete_expense/<int:expense_id>/",views.delete_expense,name="delete_expense"),
    path("add_income/",views.add_income,name="add_income"),
    path("display_income/",views.display_income,name="display_income"),
    path("edit_income/<int:income_id>/",views.edit_income,name="edit_income"),
    path("delete_income/<int:income_id>/",views.delete_income,name="delete_income")
    
]
