import os, csv
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import TimeField
from django.db.models.functions import Cast

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from .models import Trip, City, Ticket, Payment, UserProfile

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


@login_required
def export_csv(request):
    if not request.user.is_staff:
        return HttpResponse("У вас нет прав на это действие", status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ticket_sales_report.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    writer.writerow([
        'ID билета', 'Аккаунт', 'Пассажир (ФИО)',
        'Паспорт', 'Маршрут', 'Дата поездки', 'Место', 'Цена'
    ])

    tickets = Ticket.objects.select_related('passenger', 'trip').all().order_by('-booking_date')

    for t in tickets:
        writer.writerow([
            t.id,
            t.passenger.username,
            f"{t.last_name} {t.first_name} {t.patronymic}",
            t.passport_series_number,
            f"{t.trip.route}",
            t.travel_date.strftime("%d.%m.%Y"),
            t.seat_number,
            f"{t.trip.price} руб."
        ])

    return response

@login_required
def export_pdf(request):
    if not request.user.is_staff:
        return HttpResponse("Доступ запрещен", status=403)

    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    font_name = 'ArialRus'
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    else:
        return HttpResponse("Шрифт не найден")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4), margin=(20, 20, 20, 20))
    elements = []
    styles = getSampleStyleSheet()

    title_st = ParagraphStyle('Title', fontName=font_name, fontSize=16, spaceAfter=10)
    norm_st = ParagraphStyle('Normal', fontName=font_name, fontSize=9, color=colors.grey)

    msk = timezone.now() + timedelta(hours=3)
    elements.append(Paragraph("Отчёт по продаже билетов", title_st))
    elements.append(Paragraph(f"Автовокзал Онлайн  |  Дата: {msk.strftime('%d.%m.%Y %H:%M')} МСК", norm_st))
    elements.append(Spacer(1, 15))

    data = [["ID", "АККАУНТ", "ПАССАЖИР (ФИО)", "ПАСПОРТ", "РЕЙС / МАРШРУТ", "ДАТА", "МЕСТО", "СУММА"]]
    tickets = Ticket.objects.all().order_by('-booking_date')

    for t in tickets:
        data.append([
            t.id, t.passenger.username, f"{t.last_name} {t.first_name} {t.patronymic}",
            t.passport_series_number, str(t.trip.route), t.travel_date.strftime("%d.%m.%Y"),
            t.seat_number, f"{t.trip.price} р."
        ])

    table = Table(data, colWidths=[30, 60, 160, 90, 250, 70, 45, 65])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.lightgrey),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (4, -1), 'LEFT'),
        ('ALIGN', (5, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Whiter(colors.lightgrey, 0.1)]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Всего продано билетов: {tickets.count()}", norm_st))

    doc.build(elements)
    return response