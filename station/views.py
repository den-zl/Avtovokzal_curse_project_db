from .models import Trip, City, Ticket, Payment, UserProfile, Route
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, TimeField
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import datetime
import random



def index(request):
    from_city = request.GET.get('from_city')
    to_city = request.GET.get('to_city')
    travel_date = request.GET.get('date')

    trips = Trip.objects.all()

    now = timezone.now()
    today = now.date()

    if travel_date:
        search_date = datetime.strptime(travel_date, '%Y-%m-%d').date()

        if search_date < today:
            trips = trips.none()

        elif search_date == today:
            trips = trips.filter(departure_time__time__gt=now.time())

        else:
            pass
    else:
        trips = trips.filter(departure_time__time__gt=now.time())

    if from_city:
        trips = trips.filter(route__start_point__city__name__icontains=from_city)

    if to_city:
        trips = trips.filter(route__end_point__city__name__icontains=to_city)

    cities = City.objects.all()

    trips_sorted = trips.annotate(
        just_time=Cast('departure_time', TimeField())
    ).order_by('just_time')

    context = {
        'trips': trips_sorted,
        'cities': cities,
    }
    return render(request, 'station/index.html', context)

def bus_schedule(request):
    all_trips = Trip.objects.all()

    all_trips = all_trips.annotate(
        just_time=Cast('departure_time', TimeField())
    ).order_by('just_time')

    return render(request, 'station/schedule.html', {'all_trips': all_trips})

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
def checkout(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    date_input = request.POST.get('travel_date') or request.GET.get('date')

    if not date_input or date_input == "" or date_input == "None":
        travel_date = timezone.now().date()
    else:
        travel_date = date_input

    if request.method == 'POST':
        ticket = Ticket.objects.create(
            trip=trip,
            passenger=request.user,
            last_name=request.POST.get('last_name'),
            first_name=request.POST.get('first_name'),
            patronymic=request.POST.get('patronymic'),
            passport_series_number=request.POST.get('document'),
            seat_number=request.POST.get('seat'),
            travel_date=travel_date
        )
        Payment.objects.create(ticket=ticket, amount=trip.price, is_paid=True)
        return redirect('profile')

    booked_seats = Ticket.objects.filter(trip=trip, travel_date=travel_date).values_list('seat_number', flat=True)
    available_seats = [s for s in range(1, 51) if s not in booked_seats]

    return render(request, 'station/checkout.html', {
        'trip': trip,
        'seats': available_seats,
        'selected_date': travel_date
    })

@login_required
def profile(request):

    tickets = Ticket.objects.filter(passenger=request.user).order_by('-booking_date')
    return render(request, 'station/profile.html', {'tickets': tickets})

def rules(request):
    return render(request, 'station/rules.html')

def services(request):
    return render(request, 'station/services.html')

def benefits(request):
    return render(request, 'station/info.html', {'title': 'Льготы'})

def maps(request):
    return render(request, 'station/maps.html')

def support(request):
    return render(request, 'station/support.html')

def refund(request):
    return render(request, 'station/refund_page.html')

def contacts(request):
    return render(request, 'station/contacts.html')