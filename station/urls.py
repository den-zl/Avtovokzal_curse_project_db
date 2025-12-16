from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Главная страница
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')), # login/logout
]