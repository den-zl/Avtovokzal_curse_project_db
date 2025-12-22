from django.db import models
from django.contrib.auth.models import User

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название города")
    region = models.CharField(max_length=100, verbose_name="Регион", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

class BusModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="Марка/модель автобуса")
    capacity = models.PositiveIntegerField(verbose_name="Количество пассажирских мест")

    def __str__(self):
        return f"{self.name} (мест: {self.capacity})"

    class Meta:
        verbose_name = "Модель автобуса"
        verbose_name_plural = "Модели автобусов"

class Bus(models.Model):
    model = models.ForeignKey(BusModel, on_delete=models.PROTECT, verbose_name="Модель")
    reg_number = models.CharField(max_length=20, unique=True, verbose_name="Государственный номер")
    year_out = models.IntegerField(verbose_name="Год выпуска", blank=True, null=True)

    def __str__(self):
        return f"{self.reg_number} — {self.model.name}"

    class Meta:
        verbose_name = "Автобус"
        verbose_name_plural = "Автобусы"

class Driver(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="ФИО водителя")
    license_number = models.CharField(max_length=50, unique=True, verbose_name="Номер удостоверения")
    phone = models.CharField(max_length=20, verbose_name="Контактный телефон")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"

class BusStation(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название вокзала/станции")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    address = models.CharField(max_length=255, verbose_name="Точный адрес")

    def __str__(self):
        return f"{self.name} ({self.city.name})"

    class Meta:
        verbose_name = "Автовокзал"
        verbose_name_plural = "Автовокзалы"

class Route(models.Model):
    start_point = models.ForeignKey(BusStation, related_name='route_starts', on_delete=models.CASCADE, verbose_name="Откуда")
    end_point = models.ForeignKey(BusStation, related_name='route_ends', on_delete=models.CASCADE, verbose_name="Куда")
    distance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Расстояние (км)")

    def __str__(self):
        return f"Маршрут: {self.start_point} — {self.end_point}"

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, verbose_name="Маршрут")
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, verbose_name="Автобус")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, verbose_name="Водитель")
    departure_time = models.DateTimeField(verbose_name="Время отправления")
    arrival_time = models.DateTimeField(verbose_name="Время прибытия")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена билета")
    platform = models.IntegerField(default=1, verbose_name="Платформа")

    STATUS_CHOICES = (
        ('open', 'Открыт'),
        ('sent', 'Отправлен'),
        ('cancelled', 'Отменён перевозчиком'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Состояние")

    def __str__(self):
        return f"{self.route} ({self.departure_time.strftime('%H:%M')})"

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Пассажир'),
        ('manager', 'Диспетчер'),
        ('admin', 'Администратор'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client', verbose_name="Роль в системе")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон пассажира")

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class Ticket(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name="Рейс")
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пассажир")
    seat_number = models.PositiveIntegerField(verbose_name="Номер места в автобусе")
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время покупки")

    def __str__(self):
        return f"Билет №{self.id} (Место {self.seat_number})"

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"

class Payment(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, verbose_name="К билету №")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма к оплате")
    is_paid = models.BooleanField(default=False, verbose_name="Статус оплаты")
    paid_at = models.DateTimeField(auto_now=True, verbose_name="Время последнего изменения")

    def __str__(self):
        status = "Оплачено" if self.is_paid else "Не оплачено"
        return f"Оплата билета {self.ticket.id} — {status}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name="Поездка")
    rating = models.PositiveSmallIntegerField(verbose_name="Оценка (1-5)")
    comment = models.TextField(verbose_name="Текст отзыва", blank=True)

    def __str__(self):
        return f"Отзыв от {self.user.username} на рейс {self.trip.id}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"