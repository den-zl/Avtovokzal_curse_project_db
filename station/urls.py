from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Главная страница
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')), # login/logout
    path('buy/<int:trip_id>/', views.buy_ticket, name='buy_ticket'),  # Ссылка на покупку
    path('profile/', views.profile, name='profile'),  # Личный кабинет
]