"""Repeatable relative-date fictional fixtures; never callable from public routes."""
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from core.models import (Property,Household,Membership,Invitation,Vehicle,Bay,Charger,Tariff,
                         Reservation,BookingMutation,ChargingSession,Invoice,InvoiceLine)
from core.services import ingest_session, issue_invoice, parse_local


def month_shift(date, offset):
    index = date.year * 12 + date.month - 1 + offset
    return date.replace(year=index//12,month=index%12+1,day=1,hour=0,minute=0,second=0,microsecond=0)


class Command(BaseCommand):
    help = 'Seed fictional demo records relative to now (or --date ISO timestamp). Requires VOLTO_DEMO=1.'
    def add_arguments(self, parser):
        parser.add_argument('--date', help='Reference ISO date/time; local times use Europe/Zurich.')
        parser.add_argument('--reset', action='store_true', help='Delete ONLY an existing isolated fictional demo dataset before seeding.')

    @transaction.atomic
    def handle(self,*args,**options):
        if not settings.DEMO_MODE:
            raise CommandError('Demo seeding is disabled. Explicitly set VOLTO_DEMO=1 for an isolated demo database.')
        names=['alex','sam','jordan','taylor']
        User=get_user_model()
        if options['reset']:
            if Property.objects.exclude(name='Lindenhof (demo)').exists() or User.objects.exclude(username__in=names).exists():
                raise CommandError('Reset refused: this database contains records outside the known demo dataset. Use a fresh isolated demo database.')
            for model in [InvoiceLine,Invoice,BookingMutation,ChargingSession,Reservation,Invitation,Membership,Vehicle,Tariff,Charger,Bay,Household,Property]:
                model.objects.all().delete()
            User.objects.filter(username__in=names).delete()
        if Property.objects.exists():
            self.stdout.write('Data already exists; nothing changed. Use --reset only on an isolated demo database.')
            return
        zone=ZoneInfo('Europe/Zurich')
        at=parse_local(options['date'],'Europe/Zurich') if options['date'] else timezone.now()
        now=at.astimezone(zone)
        property=Property.objects.create(name='Lindenhof (demo)')
        main=Household.objects.create(property=property,name='Alex & Sam',apartment='A-12')
        other=Household.objects.create(property=property,name='Jordan household',apartment='A-07')
        users={}
        for username,first in [('alex','Alex'),('sam','Sam'),('jordan','Jordan'),('taylor','Taylor')]:
            user=User.objects.create(username=username,email=f'{username}@example.test',first_name=first)
            user.set_unusable_password();user.save(update_fields=['password']);users[username]=user
        Membership.objects.create(user=users['alex'],household=main,role='owner')
        Membership.objects.create(user=users['sam'],household=main,role='member')
        Membership.objects.create(user=users['jordan'],household=other,role='owner')
        city=Vehicle.objects.create(household=main,name='City EV',plate='DEMO001',make_model='Fictional city car',driver=users['alex'],connector='Type 2',battery_kwh=Decimal('50'))
        family=Vehicle.objects.create(household=main,name='Family EV',plate='DEMO002',make_model='Fictional family car',driver=users['sam'],connector='Type 2',battery_kwh=Decimal('70'))
        foreign=Vehicle.objects.create(household=other,name='Jordan EV',plate='DEMO003',driver=users['jordan'],connector='Type 2')
        bays=[Bay.objects.create(property=property,label=f'P{i+1:02}',row=i//10,column=i%10) for i in range(20)]
        chargers=[]
        for index,(bay_index,status) in enumerate([(2,'available'),(3,'charging'),(4,'available'),(12,'available'),(13,'offline')],1):
            chargers.append(Charger.objects.create(property=property,bay=bays[bay_index],name=f'C{index:02}',status=status,updated_at=at,connector='Type 2',max_power_kw=Decimal('11')))
        Tariff.objects.create(property=property,rate_chf=Decimal('0.3200'),effective_from=month_shift(now,-4))
        # Older records are intentionally independent of the provided old kit's fixed clock.
        for offset in [-3,-2,-1]:
            month=month_shift(now,offset)
            for n,(day,energy) in enumerate([(3,'12.000'),(8,'14.500'),(15,'18.000')]):
                start=month.replace(day=day,hour=18);end=start+timedelta(hours=2)
                car=city if n%2==0 else family
                booking=Reservation.objects.create(household=main,creator=car.driver,vehicle=car,charger=chargers[n%2],start=start,end=end,status='active')
                ingest_session(dict(provider_event=f'demo-{month:%Y-%m}-{n}',vehicle_id=car.pk,charger_id=chargers[n%2].pk,reservation_id=booking.pk,start=start.isoformat(),end=end.isoformat(),energy_kwh=energy))
            issue_at=month_shift(month,1)+timedelta(hours=10) if offset < -1 else at
            invoice=issue_invoice(main,f'{month:%Y-%m}',at=issue_at)
            if offset==-3:
                invoice.status='paid';invoice.paid_at=issue_at+timedelta(days=5);invoice.save(update_fields=['status','paid_at'])
        # Current/recent completed sessions remain unbilled. Even a seed on day 1 is valid.
        for n,energy in enumerate(['8.500','11.250','15.000']):
            end=(now-timedelta(hours=1+24*n)).replace(minute=(now.minute//30)*30,second=0,microsecond=0)
            start=end-timedelta(hours=2)
            if end.month != now.month:
                continue
            car=city if n%2==0 else family
            booking=Reservation.objects.create(household=main,creator=car.driver,vehicle=car,charger=chargers[0],start=start,end=end,status='active')
            ingest_session(dict(provider_event=f'demo-current-{n}-{now:%Y-%m}',vehicle_id=car.pk,charger_id=chargers[0].pk,reservation_id=booking.pk,start=start.isoformat(),end=end.isoformat(),energy_kwh=energy))
        tomorrow=(now+timedelta(days=1)).replace(hour=18,minute=0,second=0,microsecond=0)
        Reservation.objects.create(household=main,creator=users['alex'],vehicle=city,charger=chargers[2],start=tomorrow,end=tomorrow+timedelta(hours=2),status='active')
        Reservation.objects.create(household=main,creator=users['sam'],vehicle=family,charger=chargers[0],start=tomorrow+timedelta(days=1),end=tomorrow+timedelta(days=1,hours=1),status='active')
        cancelled=(now-timedelta(days=2)).replace(minute=(now.minute//30)*30,second=0,microsecond=0)
        Reservation.objects.create(household=main,creator=users['alex'],vehicle=city,charger=chargers[0],start=cancelled,end=cancelled+timedelta(hours=1),status='cancelled')
        rounded=now.replace(minute=(now.minute//30)*30,second=0,microsecond=0)
        Reservation.objects.create(household=other,creator=users['jordan'],vehicle=foreign,charger=chargers[3],start=rounded-timedelta(minutes=30),end=rounded+timedelta(minutes=60),status='active')
        ingest_session(dict(provider_event='demo-active-other',vehicle_id=foreign.pk,charger_id=chargers[1].pk,start=(at-timedelta(minutes=15)).isoformat(),expected_end=(at+timedelta(minutes=45)).isoformat(),energy_kwh='2.500',status='active'))
        self.stdout.write(self.style.SUCCESS(f'Seeded fictional demo at {now.isoformat()}: 2 households, 4 unusable-password demo identities, 3 vehicles, 20 bays, 5 chargers.'))
        self.stdout.write('Main demo: alex (owner), sam (member). Other household: jordan. Unassigned invitation recipient: taylor@example.test. No emails sent; no charger or payment integration.')
