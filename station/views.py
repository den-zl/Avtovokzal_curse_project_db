from django.shortcuts import render
from .models import Trip, City, Ticket, Payment, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Trip, Ticket, Payment
import random

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
            UserProfile.objects.create(user=user, role='client')
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
@login_required
def buy_ticket(request, trip_id):
    trip = Trip.objects.get(id=trip_id)

    ticket = Ticket.objects.create(
        trip=trip,
        passenger=request.user,
        seat_number=random.randint(1, 50)
    )

    Payment.objects.create(ticket=ticket, amount=trip.price, is_paid=True)

    return redirect('profile')

@login_required
def profile(request):

    tickets = Ticket.objects.filter(passenger=request.user).order_by('-booking_date')
    return render(request, 'station/profile.html', {'tickets': tickets})