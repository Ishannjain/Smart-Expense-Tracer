from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("categories/",views.categories_list,name="categories_list"),
    path("add_expnese/",views.add_expense,name="add_expense"),
    path("display_expnese/",views.display_expense,name="display_expense")
    
]
