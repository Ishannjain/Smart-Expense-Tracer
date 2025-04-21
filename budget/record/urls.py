from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static


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
    path("delete_income/<int:income_id>/",views.delete_income,name="delete_income"),
    path("create_budget/",views.create_budget,name="create_budget"),
    path("display_budget/",views.display_budget,name="display_budget"),
    path('budget/<int:budget_id>/edit/', views.edit_budget, name='edit_budget'),
    path('budget/<int:budget_id>/delete/', views.delete_budget, name='delete_budget'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('add_friend/<int:user_id>/', views.add_friend, name='add_friend'),
    path('profile_view/<int:user_id>/', views.profile_view, name='profile_view')
    
    
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)