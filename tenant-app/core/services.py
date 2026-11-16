"""Transactional booking and immutable billing boundaries; no hardware control.

SQLite connections use BEGIN IMMEDIATE (configured in settings), acquiring the
writer lock before conflict reads. A future PostgreSQL adapter must take a
property-row lock (the select_for_update below already provides that lock).
"""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import (Property, Membership, Vehicle, Charger, Reservation, BookingMutation,
                     Tariff, ChargingSession, Invoice, InvoiceLine)


class DomainError(Exception):
    def __init__(self, message, fields=None):
        super().__init__(message)
        self.message = message
        self.fields = fields or {}


def parse_local(value, zone):
    """Parse explicit offsets or reject ambiguous/nonexistent naive local times."""
    try:
        tz = ZoneInfo(str(zone))
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (ValueError, TypeError, ZoneInfoNotFoundError):
        raise DomainError('Enter a valid date and time.')
    if parsed.tzinfo is not None:
        return parsed.astimezone(dt_timezone.utc)
    candidates = []
    for fold in (0, 1):
        candidate = parsed.replace(tzinfo=tz, fold=fold)
        utc = candidate.astimezone(dt_timezone.utc)
        if utc.astimezone(tz).replace(tzinfo=None) == parsed and utc not in candidates:
            candidates.append(utc)
    if not candidates:
        raise DomainError('This local time does not exist because the clocks change. Choose another time.')
    if len(candidates) > 1:
        raise DomainError('This local time occurs twice because the clocks change. Use an explicit UTC offset or choose another time.')
    return candidates[0]


def current_tariff(property, at=None):
    at = at or timezone.now()
    tariff = Tariff.objects.filter(property=property, effective_from__lte=at).filter(Q(effective_to__isnull=True)|Q(effective_to__gt=at)).order_by('-effective_from','-pk').first()
    if not tariff:
        raise DomainError('No charging tariff is configured for this time. Please contact the property operator.')
    return tariff


def active_session_until(charger, at=None):
    """Unconfirmed release: block near-now, never claim the bay is physically free."""
    at = at or timezone.now()
    active = list(ChargingSession.objects.filter(charger=charger, status='active', start__lte=at))
    if charger.status != 'charging' and not active:
        return None
    candidates = [at + timedelta(minutes=30)]
    candidates += [s.expected_end for s in active if s.expected_end and s.expected_end > at]
    return max(candidates)


def _member(household, user):
    if not user.is_authenticated or not Membership.objects.filter(household=household,user=user,active=True).exists():
        raise DomainError('You no longer have access to this household.')


def _id(value):
    try:
        result = int(value)
        if str(result) != str(value) or result < 1:
            raise ValueError
        return result
    except (TypeError, ValueError):
        raise DomainError('Choose a valid vehicle and charger.')


@transaction.atomic
def book(household, user, data, reservation_id=None):
    _member(household, user)
    property = Property.objects.select_for_update().get(pk=household.property_id)
    request_id = str(data.get('request_id') or '').strip()
    if not request_id or len(request_id) > 128:
        raise DomainError('A request ID is required. Refresh the booking form and try again.')
    operation = 'create' if reservation_id is None else f'edit:{reservation_id}'
    payload = {key:data.get(key) for key in ('vehicle_id','charger_id','start','end')}
    digest = hashlib.sha256(json.dumps(payload,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
    prior = BookingMutation.objects.filter(household=household,request_id=request_id).select_related('reservation').first()
    if prior:
        if prior.operation != operation or prior.payload_hash != digest:
            raise DomainError('This request ID was already used for a different booking. Start a new request.')
        return prior.reservation
    now = timezone.now()
    reservation = None
    if reservation_id is not None:
        reservation = Reservation.objects.filter(pk=reservation_id,household=household).first()
        if not reservation:
            raise DomainError('Reservation not found.')
        if reservation.status != 'active' or reservation.start <= now:
            raise DomainError('Only future, active reservations can be changed.')
    vehicle = Vehicle.objects.filter(pk=_id(data.get('vehicle_id')),household=household,archived=False).first()
    charger = Charger.objects.filter(pk=_id(data.get('charger_id')),property=property).select_related('bay').first()
    if not vehicle:
        raise DomainError('Choose an active vehicle in your household.', {'vehicle_id':'Vehicle is unavailable.'})
    if not charger:
        raise DomainError('Choose a charger at your property.', {'charger_id':'Charger is unavailable.'})
    start, end = parse_local(data.get('start'),property.timezone), parse_local(data.get('end'),property.timezone)
    if start <= now:
        raise DomainError('The reservation must start in the future.', {'start':'Choose a future time.'})
    if end <= start:
        raise DomainError('The end must be after the start.', {'end':'Choose a later end time.'})
    for field, instant in [('start',start),('end',end)]:
        local = instant.astimezone(ZoneInfo(property.timezone))
        if local.second or local.microsecond or (local.hour*60+local.minute) % property.booking_increment:
            raise DomainError(f'Choose times in {property.booking_increment}-minute increments.', {field:'Use the configured time increment.'})
    duration = (end-start).total_seconds()/60
    if duration < property.min_minutes or duration > property.max_minutes:
        raise DomainError(f'Bookings must last between {property.min_minutes} and {property.max_minutes} minutes.')
    if start > now + timedelta(days=property.horizon_days):
        raise DomainError(f'Book no more than {property.horizon_days} days ahead.')
    if charger.status in ('offline','unknown'):
        raise DomainError('This charger is offline or its status is unknown. Choose another charger.')
    if not settings.DEMO_MODE and (now-charger.updated_at).total_seconds() > getattr(settings,'CHARGER_STALE_SECONDS',120):
        raise DomainError('Charger status is stale. Try again after the operator refreshes it.')
    if vehicle.connector.strip().casefold() != charger.connector.strip().casefold():
        raise DomainError('This vehicle connector is not compatible with the selected charger.')
    blocked_until = active_session_until(charger,now)
    if blocked_until and start < blocked_until:
        raise DomainError('Charging is still in progress. Its release time is unconfirmed; choose a later slot or another charger.')
    overlaps = Reservation.objects.filter(status='active',start__lt=end,end__gt=start)
    if reservation:
        overlaps = overlaps.exclude(pk=reservation.pk)
    if overlaps.filter(charger=charger).exists():
        raise DomainError('Another reservation now occupies this charger interval. Choose another time or charger.')
    if overlaps.filter(vehicle=vehicle).exists():
        raise DomainError('This vehicle already has an overlapping reservation.')
    # A booking is not a session: no energy, charge or invoice is created here.
    if reservation:
        reservation.vehicle, reservation.charger = vehicle, charger
        reservation.start, reservation.end = start, end
        reservation.save(update_fields=['vehicle','charger','start','end'])
    else:
        reservation = Reservation.objects.create(household=household,creator=user,vehicle=vehicle,charger=charger,start=start,end=end,request_id=request_id)
    BookingMutation.objects.create(household=household,request_id=request_id,operation=operation,payload_hash=digest,reservation=reservation)
    return reservation


@transaction.atomic
def cancel(household, reservation_id):
    Property.objects.select_for_update().get(pk=household.property_id)
    reservation = Reservation.objects.filter(pk=reservation_id,household=household).first()
    if not reservation:
        raise DomainError('Reservation not found.')
    if reservation.status == 'cancelled':
        return reservation
    if reservation.start <= timezone.now():
        raise DomainError('Only reservations that have not started can be cancelled.')
    reservation.status = 'cancelled'
    reservation.save(update_fields=['status'])
    return reservation


@transaction.atomic
def archive_vehicle(household, vehicle_id):
    Property.objects.select_for_update().get(pk=household.property_id)
    vehicle = Vehicle.objects.filter(pk=vehicle_id,household=household).first()
    if not vehicle:
        raise DomainError('Vehicle not found.')
    if Reservation.objects.filter(vehicle=vehicle,status='active',end__gt=timezone.now()).exists():
        raise DomainError('Cancel or reassign this vehicle’s current and future reservations before archiving it.')
    if ChargingSession.objects.filter(vehicle=vehicle,status='active').exists():
        raise DomainError('This vehicle has an active charging session. Archive it once charging has finished.')
    vehicle.archived = True
    vehicle.save(update_fields=['archived'])
    return vehicle


def month_bounds(period, zone):
    if not re.fullmatch(r'\d{4}-\d{2}', str(period)):
        raise DomainError('Use a billing period in YYYY-MM format.')
    try:
        year,month = map(int,period.split('-'))
        begin = datetime(year,month,1,tzinfo=ZoneInfo(zone))
        end = datetime(year+int(month==12),1 if month==12 else month+1,1,tzinfo=ZoneInfo(zone))
    except (ValueError,OverflowError):
        raise DomainError('Use a valid billing month.')
    return begin, end


@transaction.atomic
def issue_invoice(household, period, at=None):
    property = Property.objects.select_for_update().get(pk=household.property_id)
    begin,end = month_bounds(period,property.timezone)
    existing = Invoice.objects.filter(household=household,period=period).first()
    if existing:
        return existing
    at = at or timezone.now()
    if at < end:
        raise DomainError('Only a completed calendar month can be invoiced. Current-month sessions remain unbilled.')
    sessions = list(ChargingSession.objects.filter(household=household,status='completed',end__gte=begin,end__lt=end,invoice_line__isnull=True).select_related('charger__bay').order_by('end','pk'))
    if not sessions:
        return None
    invoice = Invoice.objects.create(household=household,number=f'VS-{period.replace("-", "")}-{household.pk:05d}',period=period,issued_at=at,due_date=at.astimezone(ZoneInfo(property.timezone)).date()+timedelta(days=14),total_cents=sum(s.cost_cents for s in sessions),currency=property.currency,property_name=property.name,household_name=household.name,apartment=household.apartment)
    InvoiceLine.objects.bulk_create([InvoiceLine(invoice=invoice,session=s,date=s.end.astimezone(ZoneInfo(property.timezone)).date(),vehicle=s.vehicle_name,charger=s.charger.name,bay=s.charger.bay.label,energy_kwh=s.energy_kwh,tariff_chf=s.tariff_chf,cost_cents=s.cost_cents) for s in sessions])
    return invoice


def _decimal(value, places, label, maximum):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0 or amount > Decimal(maximum):
            raise ValueError
        return amount.quantize(Decimal(places),rounding=ROUND_HALF_UP)
    except (InvalidOperation,ValueError,TypeError):
        raise DomainError(f'{label} must be a finite non-negative decimal in the supported range.')


@transaction.atomic
def ingest_session(data):
    """Trusted provider boundary; finalised event IDs are immutable/idempotent.

    Tariff is snapshotted at session start. kWh uses 3 decimals; rate 4;
    final charge = kWh × tariff × 100, rounded once HALF_UP to whole cents.
    Active events can transition to completed with the same provider_event.
    """
    event = str(data.get('provider_event') or '').strip()
    if not event or len(event)>160:
        raise DomainError('A stable provider event ID is required.')
    previous = ChargingSession.objects.filter(provider_event=event).first()
    if previous and previous.status == 'completed':
        return previous
    try:
        vehicle = Vehicle.objects.select_related('household__property','driver').get(pk=_id(data.get('vehicle_id')))
        charger = Charger.objects.select_related('property').get(pk=_id(data.get('charger_id')),property=vehicle.household.property)
    except (Vehicle.DoesNotExist,Charger.DoesNotExist):
        raise DomainError('Session vehicle and charger must belong to the same property.')
    Property.objects.select_for_update().get(pk=vehicle.household.property_id)
    household, property = vehicle.household, vehicle.household.property
    if data.get('household_id') is not None and _id(data['household_id']) != household.pk:
        raise DomainError('Session household does not match the vehicle.')
    status = data.get('status','completed')
    if status not in ('active','completed'):
        raise DomainError('Session status must be active or completed.')
    start = parse_local(data.get('start'),property.timezone)
    end = parse_local(data['end'],property.timezone) if data.get('end') else None
    if status == 'completed' and (not end or end<=start):
        raise DomainError('A completed session must have an end after its start.')
    if end and end<=start:
        raise DomainError('Session end must be after start.')
    if previous and (previous.vehicle_id!=vehicle.pk or previous.charger_id!=charger.pk or previous.start!=start):
        raise DomainError('An existing provider event cannot be moved to another vehicle, charger or start time.')
    reservation = None
    if data.get('reservation_id'):
        reservation = Reservation.objects.filter(pk=_id(data['reservation_id']),household=household,vehicle=vehicle,charger=charger).first()
        if not reservation:
            raise DomainError('Session reservation does not match its household, vehicle and charger.')
    driver = vehicle.driver
    if data.get('driver_id'):
        membership = Membership.objects.filter(user_id=_id(data['driver_id']),household=household,active=True).select_related('user').first()
        if not membership:
            raise DomainError('Session driver must be a household member.')
        driver = membership.user
    energy = _decimal(data.get('energy_kwh',0),'0.001','Energy','999999999.999')
    rate = previous.tariff_chf if previous else current_tariff(property,start).rate_chf
    cost = int((energy*rate*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    expected_end = parse_local(data['expected_end'],property.timezone) if data.get('expected_end') else None
    if expected_end and expected_end<=start:
        raise DomainError('Expected end must be after start.')
    values = dict(household=household,vehicle=vehicle,charger=charger,driver=driver,reservation=reservation,start=start,end=end,expected_end=expected_end,energy_kwh=energy,tariff_chf=rate,cost_cents=cost,status=status,vehicle_name=previous.vehicle_name if previous else vehicle.name,driver_name=previous.driver_name if previous else ((driver.get_full_name() or driver.username) if driver else ''))
    if previous:
        for key,value in values.items(): setattr(previous,key,value)
        previous.save()
        return previous
    return ChargingSession.objects.create(provider_event=event,**values)
