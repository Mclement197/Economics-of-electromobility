import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone as utc
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase, override_settings
from django.utils import timezone
from .models import Property,Household,Membership,Vehicle,Bay,Charger,Tariff,Reservation,ChargingSession,Invoice,InvoiceLine
from .services import DomainError,book,cancel,archive_vehicle,issue_invoice,ingest_session,parse_local,active_session_until


@override_settings(DEMO_MODE=True)
class DomainTests(TestCase):
    def setUp(self):
        self.now=datetime(2026,11,16,10,0,tzinfo=utc.utc)
        self.clock=patch('core.services.timezone.now',return_value=self.now);self.clock.start();self.addCleanup(self.clock.stop)
        self.property=Property.objects.create(name='Test house')
        self.household=Household.objects.create(property=self.property,name='Test household',apartment='A1')
        self.other=Household.objects.create(property=self.property,name='Other household',apartment='A2')
        self.user=get_user_model().objects.create_user(username='test-owner')
        self.foreign=get_user_model().objects.create_user(username='other-owner')
        Membership.objects.create(user=self.user,household=self.household,role='owner')
        Membership.objects.create(user=self.foreign,household=self.other,role='owner')
        self.vehicle=Vehicle.objects.create(household=self.household,name='Original car',plate='DEMO1',driver=self.user)
        self.vehicle2=Vehicle.objects.create(household=self.household,name='Second car',plate='DEMO2')
        self.foreign_car=Vehicle.objects.create(household=self.other,name='Other car',plate='DEMO3')
        self.chargers=[]
        for n in range(2):
            bay=Bay.objects.create(property=self.property,label=f'P{n}',row=0,column=n)
            self.chargers.append(Charger.objects.create(property=self.property,bay=bay,name=f'C{n}',status='available',updated_at=self.now))
        self.tariff=Tariff.objects.create(property=self.property,rate_chf=Decimal('0.3200'),effective_from=self.now-timedelta(days=120))
    def data(self,**kwargs):
        data=dict(vehicle_id=self.vehicle.pk,charger_id=self.chargers[0].pk,start='2026-11-17T10:00:00+01:00',end='2026-11-17T11:00:00+01:00',request_id='one')
        return data|kwargs
    def event(self,**kwargs):
        return dict(provider_event='event-one',vehicle_id=self.vehicle.pk,charger_id=self.chargers[0].pk,start='2026-10-03T18:00:00+02:00',end='2026-10-03T20:00:00+02:00',energy_kwh='12.000')|kwargs
    def test_book_idempotency_adjacent_and_no_charging_side_effect(self):
        first=book(self.household,self.user,self.data())
        self.assertEqual(book(self.household,self.user,self.data()).pk,first.pk)
        with self.assertRaises(DomainError): book(self.household,self.user,self.data(request_id='one',end='2026-11-17T12:00+01:00'))
        adjacent=book(self.household,self.user,self.data(request_id='adjacent',start='2026-11-17T11:00+01:00',end='2026-11-17T12:00+01:00'))
        self.assertNotEqual(first.pk,adjacent.pk)
        self.assertEqual(ChargingSession.objects.count(),0)
        self.assertEqual(Invoice.objects.count(),0)
    def test_charger_vehicle_conflicts_and_failed_edit_preserves(self):
        original=book(self.household,self.user,self.data())
        with self.assertRaisesMessage(DomainError,'charger interval'):
            book(self.other,self.foreign,self.data(request_id='other',vehicle_id=self.foreign_car.pk))
        with self.assertRaisesMessage(DomainError,'vehicle already'):
            book(self.household,self.user,self.data(request_id='vehicle',charger_id=self.chargers[1].pk))
        second=book(self.household,self.user,self.data(request_id='second',vehicle_id=self.vehicle2.pk,charger_id=self.chargers[1].pk,start='2026-11-17T12:00+01:00',end='2026-11-17T13:00+01:00'))
        with self.assertRaises(DomainError):book(self.household,self.user,self.data(request_id='bad-edit'),second.pk)
        second.refresh_from_db();self.assertEqual(second.start.hour,11);self.assertEqual(second.vehicle_id,self.vehicle2.pk)
        changed=book(self.household,self.user,self.data(request_id='good-edit',start='2026-11-17T13:00+01:00',end='2026-11-17T14:00+01:00'),original.pk)
        self.assertEqual(book(self.household,self.user,self.data(request_id='good-edit',start='2026-11-17T13:00+01:00',end='2026-11-17T14:00+01:00'),original.pk).pk,changed.pk)
    def test_booking_boundaries_permissions_and_compatibility(self):
        invalid=[dict(start='2026-11-16T10:00Z',end='2026-11-16T11:00Z'),dict(start='2026-11-17T10:15+01:00'),dict(end='2026-11-17T10:00+01:00'),dict(end='2026-11-17T19:00+01:00'),dict(start='2027-01-01T10:00+01:00',end='2027-01-01T11:00+01:00'),dict(vehicle_id=self.foreign_car.pk)]
        for case in invalid:
            with self.subTest(case=case), self.assertRaises(DomainError): book(self.household,self.user,self.data(**case))
        with self.assertRaises(DomainError):book(self.household,self.foreign,self.data())
        self.vehicle.connector='CCS';self.vehicle.save()
        with self.assertRaisesMessage(DomainError,'compatible'):book(self.household,self.user,self.data())
        self.vehicle.connector='Type 2';self.vehicle.save()
        for state in ('offline','unknown'):
            self.chargers[0].status=state;self.chargers[0].save()
            with self.assertRaisesMessage(DomainError,'offline or'):book(self.household,self.user,self.data())
    def test_cancel_frees_slot_archive_and_historical_snapshots(self):
        booking=book(self.household,self.user,self.data())
        with self.assertRaises(DomainError):archive_vehicle(self.household,self.vehicle.pk)
        with self.assertRaises(DomainError):cancel(self.other,booking.pk)
        cancel(self.household,booking.pk);cancel(self.household,booking.pk)
        book(self.other,self.foreign,self.data(request_id='freed',vehicle_id=self.foreign_car.pk))
        archive_vehicle(self.household,self.vehicle.pk)
        self.vehicle.refresh_from_db();self.assertTrue(self.vehicle.archived)
    def test_active_overrun_blocks_near_now_but_not_future_day(self):
        charger=self.chargers[0];charger.status='charging';charger.save()
        ingest_session(self.event(provider_event='active',status='active',start='2026-11-16T09:00Z',end=None,expected_end='2026-11-16T10:00Z',energy_kwh='1'))
        self.assertEqual(active_session_until(charger,self.now),self.now+timedelta(minutes=30))
        with patch('core.services.timezone.now',return_value=self.now+timedelta(minutes=10)):
            with self.assertRaisesMessage(DomainError,'in progress'):
                book(self.household,self.user,self.data(start='2026-11-16T10:30Z',end='2026-11-16T11:00Z'))
    def test_active_booking_future_valid_and_stale_status(self):
        charger=self.chargers[0];charger.status='charging';charger.save()
        book(self.household,self.user,self.data())
        with override_settings(DEMO_MODE=False):
            charger.updated_at=self.now-timedelta(minutes=3);charger.save()
            with self.assertRaisesMessage(DomainError,'stale'):
                book(self.household,self.user,self.data(request_id='stale',start='2026-11-17T12:00+01:00',end='2026-11-17T13:00+01:00'))
    def test_invoice_reconciliation_idempotence_and_snapshots(self):
        first=ingest_session(self.event())
        second=ingest_session(self.event(provider_event='event-two',energy_kwh='14.500',start='2026-10-04T18:00+02:00',end='2026-10-04T20:00+02:00'))
        self.assertEqual(first.cost_cents,384);self.assertEqual(second.cost_cents,464)
        self.assertEqual(ingest_session(self.event()).pk,first.pk)
        invoice=issue_invoice(self.household,'2026-10')
        self.assertEqual(invoice.total_cents,848)
        self.assertEqual(sum(invoice.lines.values_list('cost_cents',flat=True)),848)
        self.assertEqual(issue_invoice(self.household,'2026-10').pk,invoice.pk)
        self.vehicle.name='Renamed car';self.vehicle.save()
        self.tariff.rate_chf=Decimal('99.0000');self.tariff.save()
        first.refresh_from_db();self.assertEqual(first.cost_cents,384);self.assertEqual(first.tariff_chf,Decimal('0.3200'))
        self.assertEqual(invoice.lines.first().vehicle,'Original car')
        self.assertEqual(InvoiceLine.objects.count(),2)
        with self.assertRaisesMessage(DomainError,'completed calendar month'):issue_invoice(self.household,'2026-11')
    def test_cent_rounding_and_active_finalisation(self):
        self.tariff.rate_chf=Decimal('0.0050');self.tariff.save()
        active=ingest_session(self.event(status='active',end=None,energy_kwh='1.000'))
        self.assertEqual(active.cost_cents,1)
        self.tariff.rate_chf=Decimal('5.0000');self.tariff.save()
        final=ingest_session(self.event(energy_kwh='2.000'))
        self.assertEqual(active.pk,final.pk);self.assertEqual(final.cost_cents,1);self.assertEqual(final.status,'completed')
        self.assertEqual(final.tariff_chf,Decimal('0.0050'))
    def test_dst_and_timezone_month_boundary(self):
        for value in ['2026-03-29T02:30','2026-10-25T02:30']:
            with self.assertRaises(DomainError):parse_local(value,'Europe/Zurich')
        a=parse_local('2026-10-25T02:30+02:00','Europe/Zurich');b=parse_local('2026-10-25T02:30+01:00','Europe/Zurich')
        self.assertEqual((b-a).total_seconds(),3600)
        # UTC October end belongs to November locally and must remain unbilled now.
        s=ingest_session(self.event(start='2026-10-31T22:00Z',end='2026-10-31T23:30Z'))
        self.assertIsNone(issue_invoice(self.household,'2026-10'))
        self.assertEqual(s.end.astimezone(__import__('zoneinfo').ZoneInfo('Europe/Zurich')).month,11)


class RealConnectionConcurrencyTest(SimpleTestCase):
    def test_two_simultaneous_writers_exactly_one_wins(self):
        """File-backed SQLite, separate thread connections, real IMMEDIATE locks.

        Django's default shared in-memory SQLite tests report SQLITE_LOCKED
        immediately rather than exercising file busy-timeout behaviour.
        """
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='voltoshare-concurrency-') as directory:
            env={**os.environ,'DJANGO_SETTINGS_MODULE':'config.settings','VOLTO_DB':str(Path(directory)/'db.sqlite3'),'VOLTO_DEMO':'1','VOLTO_SECRET_KEY':'test-only-concurrency-secret','VOLTO_AXES':'0'}
            subprocess.run([sys.executable,'manage.py','migrate','--noinput','--verbosity','0'],cwd=root,env=env,check=True,capture_output=True,text=True)
            code='''
import django;django.setup()
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import connections
from django.utils import timezone
from core.models import *
from core.services import book,DomainError
p=Property.objects.create(name='Concurrency')
b=Bay.objects.create(property=p,label='P01',row=0,column=0)
c=Charger.objects.create(property=p,bay=b,name='C01',status='available')
start=(timezone.now()+timedelta(days=1)).replace(hour=12,minute=0,second=0,microsecond=0)
records=[]
for i in range(2):
 h=Household.objects.create(property=p,name=str(i),apartment=str(i));u=get_user_model().objects.create_user(username=str(i));Membership.objects.create(household=h,user=u,role='owner');v=Vehicle.objects.create(household=h,name='Car',plate=str(i));records.append((h.pk,u.pk,v.pk))
barrier=Barrier(2)
def attempt(record):
 h,u,v=record
 household=Household.objects.get(pk=h);user=get_user_model().objects.get(pk=u)
 barrier.wait()
 try:
  book(household,user,dict(vehicle_id=v,charger_id=c.pk,start=start.isoformat(),end=(start+timedelta(hours=1)).isoformat(),request_id='concurrent'))
  return 'success'
 except DomainError:return 'conflict'
 finally:connections.close_all()
with ThreadPoolExecutor(max_workers=2) as executor: result=list(executor.map(attempt,records))
assert sorted(result)==['conflict','success'],result
assert Reservation.objects.count()==1
print('one success, one conflict; one stored reservation')
'''
            result=subprocess.run([sys.executable,'-c',code],cwd=root,env=env,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('one success, one conflict',result.stdout)
