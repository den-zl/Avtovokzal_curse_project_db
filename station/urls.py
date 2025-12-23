from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Главная страница
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')), # login/logout
    path('checkout/<int:trip_id>/', views.checkout, name='checkout'), # Ссылка на покупку
    path('profile/', views.profile, name='profile'),  # Личный кабинет
    path('rules/', views.rules, name='rules'),
    path('services/', views.services, name='services'),
    path('benefits/', views.benefits, name='benefits'),
    path('maps/', views.maps, name='maps'),
    path('support/', views.support, name='support'),
    path('refund/', views.refund, name='refund'),
    path('contacts/', views.contacts, name='contacts'),
    path('schedule/', views.bus_schedule, name='bus_schedule'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
