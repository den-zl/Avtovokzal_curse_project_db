from django.shortcuts import render
from .models import Trip, City

def index(request):
    # Рейсы из базы
    trips = Trip.objects.all().order_by('departure_time')
    # Города для формы поиска
    cities = City.objects.all()

    context = {
        'trips': trips,
        'cities': cities,
    }
    return render(request, 'station/index.html', context)