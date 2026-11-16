from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.utils import timezone


class Property(models.Model):
    name = models.CharField(max_length=120)
    timezone = models.CharField(max_length=64, default='Europe/Zurich')
    currency = models.CharField(max_length=3, default='CHF')
    booking_increment = models.PositiveSmallIntegerField(default=30)
    min_minutes = models.PositiveSmallIntegerField(default=30)
    max_minutes = models.PositiveSmallIntegerField(default=480)
    horizon_days = models.PositiveSmallIntegerField(default=30)


class Household(models.Model):
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='households')
    name = models.CharField(max_length=120)
    apartment = models.CharField(max_length=40)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['property','apartment'], name='unique_property_apartment')]


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='memberships')
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='memberships')
    role = models.CharField(max_length=10, choices=[('owner','Owner'),('member','Member')], default='member')
    active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','household'], name='unique_user_household')]


class Invitation(models.Model):
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='invitations')
    email = models.EmailField()
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)


class Vehicle(models.Model):
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='vehicles')
    name = models.CharField(max_length=100)
    plate = models.CharField(max_length=30)
    make_model = models.CharField(max_length=120, blank=True)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    connector = models.CharField(max_length=40, default='Type 2')
    battery_kwh = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    archived = models.BooleanField(default=False)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(battery_kwh__isnull=True)|Q(battery_kwh__gt=0), name='positive_battery_capacity')]


class Bay(models.Model):
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='bays')
    label = models.CharField(max_length=20)
    row = models.PositiveSmallIntegerField()
    column = models.PositiveSmallIntegerField()
    class Meta:
        constraints = [models.UniqueConstraint(fields=['property','label'], name='unique_bay_label'), models.UniqueConstraint(fields=['property','row','column'], name='unique_bay_position')]


class Charger(models.Model):
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='chargers')
    bay = models.OneToOneField(Bay, on_delete=models.PROTECT, related_name='charger')
    name = models.CharField(max_length=60)
    connector = models.CharField(max_length=40, default='Type 2')
    max_power_kw = models.DecimalField(max_digits=6, decimal_places=2, default='11.00')
    status = models.CharField(max_length=12, choices=[('available','Available'),('charging','Charging'),('offline','Offline'),('unknown','Unknown')], default='unknown')
    updated_at = models.DateTimeField(default=timezone.now)


class Tariff(models.Model):
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='tariffs')
    rate_chf = models.DecimalField(max_digits=9, decimal_places=4)
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(rate_chf__gte=0), name='nonnegative_tariff'), models.CheckConstraint(condition=Q(effective_to__isnull=True)|Q(effective_to__gt=F('effective_from')), name='tariff_date_order')]


class Reservation(models.Model):
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='reservations')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='reservations')
    charger = models.ForeignKey(Charger, on_delete=models.PROTECT, related_name='reservations')
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=12, choices=[('active','Active'),('cancelled','Cancelled')], default='active')
    request_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(end__gt=F('start')), name='reservation_date_order')]
        indexes = [models.Index(fields=['charger','status','start','end']), models.Index(fields=['vehicle','status','start','end'])]


class BookingMutation(models.Model):
    household = models.ForeignKey(Household, on_delete=models.PROTECT)
    request_id = models.CharField(max_length=128)
    operation = models.CharField(max_length=60)
    payload_hash = models.CharField(max_length=64)
    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['household','request_id'], name='unique_booking_mutation')]


class ChargingSession(models.Model):
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='sessions')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='sessions')
    charger = models.ForeignKey(Charger, on_delete=models.PROTECT, related_name='sessions')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT, null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True, db_index=True)
    expected_end = models.DateTimeField(null=True, blank=True)
    energy_kwh = models.DecimalField(max_digits=12, decimal_places=3)
    tariff_chf = models.DecimalField(max_digits=9, decimal_places=4)
    cost_cents = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=12, choices=[('completed','Completed'),('active','Active')])
    provider_event = models.CharField(max_length=160, unique=True)
    vehicle_name = models.CharField(max_length=100)
    driver_name = models.CharField(max_length=150, blank=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(energy_kwh__gte=0), name='nonnegative_session_energy'), models.CheckConstraint(condition=Q(tariff_chf__gte=0), name='nonnegative_session_tariff'), models.CheckConstraint(condition=Q(end__isnull=True)|Q(end__gt=F('start')), name='session_date_order'), models.CheckConstraint(condition=Q(status='active')|Q(end__isnull=False), name='completed_session_has_end')]


class Invoice(models.Model):
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='invoices')
    number = models.CharField(max_length=64, unique=True)
    period = models.CharField(max_length=7)
    issued_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    total_cents = models.PositiveBigIntegerField()
    status = models.CharField(max_length=8, choices=[('paid','Paid'),('unpaid','Unpaid')], default='unpaid')
    paid_at = models.DateTimeField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='CHF')
    property_name = models.CharField(max_length=120)
    household_name = models.CharField(max_length=120)
    apartment = models.CharField(max_length=40)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['household','period'], name='unique_household_invoice_period')]


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='lines')
    session = models.OneToOneField(ChargingSession, on_delete=models.PROTECT, related_name='invoice_line')
    date = models.DateField()
    vehicle = models.CharField(max_length=100)
    charger = models.CharField(max_length=60)
    bay = models.CharField(max_length=20)
    energy_kwh = models.DecimalField(max_digits=12, decimal_places=3)
    tariff_chf = models.DecimalField(max_digits=9, decimal_places=4)
    cost_cents = models.PositiveBigIntegerField()
