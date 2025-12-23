from django.contrib import admin
from .models import (
    City, BusModel, Bus, Driver, BusStation,
    Route, Trip, UserProfile, Ticket, Payment, Review
)

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