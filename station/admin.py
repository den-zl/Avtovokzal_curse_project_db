from django.contrib import admin
# Импорт всех моделей из models.py
from .models import (
    City, BusModel, Bus, Driver, BusStation,
    Route, Trip, UserProfile, Ticket, Payment, Review
)

# Регистрация каждой модели, чтобы она появилась в интерфейсе
admin.site.register(City)
admin.site.register(BusModel)
admin.site.register(Bus)
admin.site.register(Driver)
admin.site.register(BusStation)
admin.site.register(Route)
admin.site.register(Trip)
admin.site.register(UserProfile)
admin.site.register(Ticket)
admin.site.register(Payment)
admin.site.register(Review)