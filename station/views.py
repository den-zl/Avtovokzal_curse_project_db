from django.shortcuts import render
from .models import Trip, City, Ticket, Payment, UserProfile, Route
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import random

def index(request):
    from_city = request.GET.get('from_city')
    to_city = request.GET.get('to_city')
    travel_date = request.GET.get('date')

    trips = Trip.objects.all()

    if from_city:
        trips = trips.filter(route__start_point__city__name__icontains=from_city)

    if to_city:
        trips = trips.filter(route__end_point__city__name__icontains=to_city)

    if travel_date:
        trips = trips.filter(departure_time__date=travel_date)
    cities = City.objects.all()

    context = {
        'trips': trips.order_by('departure_time'),
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

def rules(request):
    return render(request, 'station/info.html', {'title': 'Правила проезда'})

def services(request):
    return render(request, 'station/info.html', {'title': 'Дополнительные услуги'})

def benefits(request):
    return render(request, 'station/info.html', {'title': 'Льготы'})

def maps(request):
    return render(request, 'station/info.html', {'title': 'Схемы автовокзалов'})

def refund(request):
    return render(request, 'station/info.html', {'title': 'Возврат билета'})