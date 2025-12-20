from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Главная страница
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')), # login/logout
    path('buy/<int:trip_id>/', views.buy_ticket, name='buy_ticket'),  # Ссылка на покупку
    path('profile/', views.profile, name='profile'),  # Личный кабинет
    path('rules/', views.rules, name='rules'),
    path('services/', views.services, name='services'),
    path('benefits/', views.benefits, name='benefits'),
    path('maps/', views.maps, name='maps'),
    path('refund/', views.refund, name='refund'),
    path('support/', views.support, name='support'),
    path('refund/', views.refund, name='refund'),
]
