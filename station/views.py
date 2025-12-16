from django.shortcuts import render
from .models import Trip, City
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect

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

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})