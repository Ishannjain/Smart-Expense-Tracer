from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("categories/", views.categories_list, name="categories_list"),
    path("add_expense/", views.add_expense, name="add_expense"),
    path("display_expense/", views.display_expense, name="display_expense"),
    path("edit_expense/<int:expense_id>/", views.edit_expense, name="edit_expense"),
    path("delete_expense/<int:expense_id>/", views.delete_expense, name="delete_expense"),
    path("add_income/", views.add_income, name="add_income"),
    path("display_income/", views.display_income, name="display_income"),
    path("edit_income/<int:income_id>/", views.edit_income, name="edit_income"),
    path("delete_income/<int:income_id>/", views.delete_income, name="delete_income"),
    path("create_budget/", views.create_budget, name="create_budget"),
    path("display_budget/", views.display_budget, name="display_budget"),
    path('budget/<int:budget_id>/edit/', views.edit_budget, name='edit_budget'),
    path('budget/<int:budget_id>/delete/', views.delete_budget, name='delete_budget'),
    path('connect/find/', views.find_users, name='find_users'),
    path('connect/toggle/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    path('profile_view/<int:user_id>/', views.profile_view, name='profile_view'),
    path('chat_view/<int:user_id>/', views.chat_view, name='chat_view'),
    path('edit_profile/<int:user_id>/', views.edit_profile, name='edit_profile'),
    path('rooms/', views.split_rooms, name='split_rooms'),
    
    path('rooms/create/', views.create_room, name='create_room'),
    path('rooms/<str:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<str:room_id>/add-member/', views.add_member, name='add_member'),
    path('rooms/<str:room_id>/add-expense/', views.add_group_expense, name='add_group_expense'),
    path('rooms/<str:room_id>/settle/', views.settle_up, name='settle_up'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)