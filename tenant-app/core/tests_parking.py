"""Bay bookings, floor metadata, preservation and concurrent ordinary-space safety."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone as utc
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase, override_settings
from .models import (Property, Household, Membership, Vehicle, Bay, Charger,
                     Reservation, BookingMutation, ChargingSession, Invoice, Tariff)
from .services import book, cancel, DomainError, ingest_session


@override_settings(DEMO_MODE=True, AXES_ENABLED=False)
class ParkingBayTests(TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 24, 12, tzinfo=utc.utc)
        self.clock = patch('core.services.timezone.now', return_value=self.now)
        self.clock.start(); self.addCleanup(self.clock.stop)
        self.property = Property.objects.create(name='Test garage')
        self.household = Household.objects.create(property=self.property, name='Resident', apartment='A1')
        self.other = Household.objects.create(property=self.property, name='Other', apartment='A2')
        self.user = get_user_model().objects.create(username='parking-owner')
        self.foreign = get_user_model().objects.create(username='parking-other')
        Membership.objects.create(user=self.user, household=self.household)
        Membership.objects.create(user=self.foreign, household=self.other)
        self.vehicle = Vehicle.objects.create(household=self.household, name='Car', plate='TEST')
        self.foreign_car = Vehicle.objects.create(household=self.other, name='Private', plate='SECRET')
        self.ordinary = Bay.objects.create(property=self.property, label='UG1-01', row=0, column=0)
        self.upper = Bay.objects.create(property=self.property, label='UG2-01', floor='UG2', row=0, column=0)
        self.charged = Bay.objects.create(property=self.property, label='UG1-02', row=0, column=1)
        self.charger = Charger.objects.create(property=self.property, bay=self.charged, name='C1', status='available')
        Tariff.objects.create(property=self.property, rate_chf='0.3200', effective_from=self.now-timedelta(days=50))

    def data(self, **overrides):
        return dict(bay_id=self.ordinary.id, vehicle_id=self.vehicle.id,
                    start='2026-11-25T10:00+01:00', end='2026-11-25T11:00+01:00', request_id='parking') | overrides

    def test_ordinary_booking_without_tariff_or_connector_creates_no_charge(self):
        Tariff.objects.all().delete()
        self.vehicle.connector='CCS';self.vehicle.save()
        with override_settings(DEMO_MODE=False):
            r=book(self.household,self.user,self.data())
        self.assertIsNone(r.charger_id);self.assertEqual(r.bay_id,self.ordinary.pk)
        self.assertEqual(book(self.household,self.user,self.data()).pk,r.pk)
        self.assertEqual(ChargingSession.objects.count(),0);self.assertEqual(Invoice.objects.count(),0)
        with self.assertRaises(DomainError):
            book(self.household,self.user,self.data(bay_id=self.upper.pk))

    def test_same_coordinates_different_floors_independent_but_vehicle_shared(self):
        first=book(self.household,self.user,self.data())
        second=book(self.other,self.foreign,self.data(bay_id=self.upper.id,vehicle_id=self.foreign_car.id))
        self.assertNotEqual(first.bay_id,second.bay_id)
        with self.assertRaisesMessage(DomainError,'parking bay interval'):
            book(self.other,self.foreign,self.data(vehicle_id=self.foreign_car.id,request_id='conflict'))
        with self.assertRaisesMessage(DomainError,'vehicle already'):
            book(self.household,self.user,self.data(bay_id=self.charged.id,request_id='vehicle'))

    def test_edit_cancel_and_failed_edit_keep_original(self):
        r=book(self.household,self.user,self.data())
        occupied=book(self.other,self.foreign,self.data(bay_id=self.upper.id,vehicle_id=self.foreign_car.id))
        with self.assertRaises(DomainError):
            book(self.household,self.user,self.data(bay_id=self.upper.id,request_id='failed'),r.pk)
        r.refresh_from_db();self.assertEqual(r.bay_id,self.ordinary.id)
        changed=book(self.household,self.user,self.data(bay_id=self.charged.id,request_id='change'),r.pk)
        self.assertEqual(changed.charger_id,self.charger.id)
        changed=book(self.household,self.user,self.data(request_id='ordinary-again'),r.pk)
        self.assertIsNone(changed.charger_id)
        cancel(self.household,r.pk)
        replacement=book(self.other,self.foreign,self.data(vehicle_id=self.foreign_car.id,request_id='reuse',start='2026-11-25T11:00+01:00',end='2026-11-25T12:00+01:00'))
        self.assertEqual(replacement.bay_id,self.ordinary.id)
        with self.assertRaises(DomainError):cancel(self.household,occupied.pk)

    def test_bay_validation_and_no_charger_check_bypass(self):
        other_property=Property.objects.create(name='Elsewhere')
        foreign_bay=Bay.objects.create(property=other_property,label='P1',row=0,column=0)
        for override in [dict(bay_id=foreign_bay.id),dict(bay_id=999999),dict(bay_id='1.5'),dict(bay_id=None),dict(bay_id=self.ordinary.id,charger_id=self.charger.id)]:
            with self.subTest(override=override),self.assertRaises(DomainError):
                book(self.household,self.user,self.data(**override))
        self.ordinary.bookable=False;self.ordinary.save()
        with self.assertRaisesMessage(DomainError,'not available for reservations'):
            book(self.household,self.user,self.data())
        self.charger.status='offline';self.charger.save()
        with self.assertRaisesMessage(DomainError,'offline'):
            book(self.household,self.user,self.data(bay_id=self.charged.id))
        self.charger.status='available';self.charger.save()
        self.vehicle.connector='CCS';self.vehicle.save()
        with self.assertRaisesMessage(DomainError,'compatible'):
            book(self.household,self.user,self.data(bay_id=self.charged.id))

    def test_legacy_creation_and_idempotency_hash_unchanged(self):
        legacy=self.data();legacy.pop('bay_id');legacy['charger_id']=self.charger.id
        r=book(self.household,self.user,legacy)
        self.assertEqual(r.bay_id,self.charged.id)
        expected=hashlib.sha256(json.dumps({k:legacy.get(k) for k in ('vehicle_id','charger_id','start','end')},sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(BookingMutation.objects.get(reservation=r).payload_hash,expected)
        fixture=Reservation.objects.create(household=self.household,creator=self.user,vehicle=self.vehicle,charger=self.charger,start=self.now-timedelta(days=2),end=self.now-timedelta(days=1))
        self.assertEqual(fixture.bay_id,self.charged.id)

    def test_api_includes_floor_and_anonymous_noncharging_occupancy(self):
        foreign=book(self.other,self.foreign,self.data(vehicle_id=self.foreign_car.id))
        self.client.force_login(self.user,backend='django.contrib.auth.backends.ModelBackend')
        with patch('core.views.timezone.now',return_value=self.now):response=self.client.get('/api/state/')
        self.assertEqual(response.status_code,200,response.content)
        data=response.json();bay=next(b for b in data['bays'] if b['id']==self.upper.id)
        self.assertEqual(bay['floor'],'UG2');self.assertTrue(bay['bookable']);self.assertIsNone(bay['charger_id'])
        occupied=next(o for o in data['occupancy'] if o['bay_id']==self.ordinary.id)
        self.assertIsNone(occupied['charger_id']);self.assertFalse(occupied['own'])
        self.assertNotIn('vehicle_id',occupied);self.assertNotIn('household_id',occupied)
        self.assertNotIn('SECRET',json.dumps(data));self.assertNotIn(foreign.id,[r['id'] for r in data['reservations']])
        own=book(self.household,self.user,self.data(bay_id=self.upper.id))
        with patch('core.views.timezone.now',return_value=self.now):data=self.client.get('/api/state/').json()
        r=next(r for r in data['reservations'] if r['id']==own.id)
        self.assertEqual(r['floor'],'UG2');self.assertEqual(r['charger_name'],'Parking only')

    def test_api_roundtrip_create_change_cancel_ordinary_bay(self):
        self.client.force_login(self.user,backend='django.contrib.auth.backends.ModelBackend')
        response=self.client.post('/api/reservations/',data=json.dumps(self.data()),content_type='application/json')
        self.assertEqual(response.status_code,200,response.content)
        reservation_id=response.json()['reservation_id']
        change=self.client.post(f'/api/reservations/{reservation_id}/change/',data=json.dumps(self.data(bay_id=self.upper.id,request_id='api-change')),content_type='application/json')
        self.assertEqual(change.status_code,200,change.content)
        with patch('core.views.timezone.now',return_value=self.now):data=self.client.get('/api/state/').json()
        saved=next(r for r in data['reservations'] if r['id']==reservation_id)
        self.assertEqual((saved['bay_id'],saved['floor'],saved['charger_id'],saved['charger_name']),(self.upper.id,'UG2',None,'Parking only'))
        response=self.client.post(f'/api/reservations/{reservation_id}/cancel/',data='{}',content_type='application/json')
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(Reservation.objects.get(pk=reservation_id).status,'cancelled')
        self.assertFalse(ChargingSession.objects.exists());self.assertFalse(Invoice.objects.exists())

    def test_ordinary_reservation_cannot_be_attached_to_charging_session(self):
        r=book(self.household,self.user,self.data())
        with self.assertRaisesMessage(DomainError,'does not match'):
            ingest_session(dict(provider_event='wrong-reservation',vehicle_id=self.vehicle.id,charger_id=self.charger.id,reservation_id=r.id,start='2026-11-25T10:00+01:00',end='2026-11-25T11:00+01:00',energy_kwh='5'))
        self.assertEqual(ChargingSession.objects.count(),0)


class ParkingConcurrencyAndMigrationTests(SimpleTestCase):
    def test_migration_preserves_old_records_then_concurrent_ordinary_booking(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='voltoshare-bay-test-') as tmp:
            env=os.environ|{'VOLTO_DB':str(Path(tmp)/'test.sqlite3'),'VOLTO_SECRET_KEY':'isolated-test-only','VOLTO_DEMO':'1','VOLTO_AXES':'0','DJANGO_SETTINGS_MODULE':'config.settings'}
            code=r'''
import django
django.setup()
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.core.management import call_command
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.utils import timezone
executor=MigrationExecutor(connections['default'])
executor.migrate([('core','0001_initial'),('auth','0012_alter_user_first_name_max_length')])
apps=executor.loader.project_state([('core','0001_initial'),('auth','0012_alter_user_first_name_max_length')]).apps
P=apps.get_model('core','Property');B=apps.get_model('core','Bay');C=apps.get_model('core','Charger');H=apps.get_model('core','Household');V=apps.get_model('core','Vehicle');R=apps.get_model('core','Reservation');U=apps.get_model('auth','User')
p=P.objects.create(name='Historical');h=H.objects.create(property=p,name='Old',apartment='A1');u=U.objects.create(username='old');v=V.objects.create(household=h,name='Old car',plate='OLD');b=B.objects.create(property=p,label='P1',row=0,column=0);c=C.objects.create(property=p,bay=b,name='C1',status='available')
now=timezone.now();r=R.objects.create(household=h,creator=u,vehicle=v,charger=c,start=now-timedelta(days=2),end=now-timedelta(days=1),request_id='preserve')
old_pk=r.pk
call_command('migrate',verbosity=0)
from core.models import Property,Household,Membership,Vehicle,Bay,Reservation
from django.contrib.auth import get_user_model
from core.services import book,DomainError
r=Reservation.objects.get(pk=old_pk)
assert r.bay_id==b.id and r.charger_id==c.id and r.request_id=='preserve'
assert r.bay.floor=='UG1' and r.bay.bookable
p=Property.objects.get(pk=p.id)
ordinary=Bay.objects.create(property=p,label='P2',row=0,column=1,floor='UG2')
records=[]
for i in range(2):
 h=Household.objects.create(property=p,name=str(i),apartment=str(i));u=get_user_model().objects.create(username=str(i));Membership.objects.create(household=h,user=u);v=Vehicle.objects.create(household=h,name='Car',plate=str(i));records.append((h.pk,u.pk,v.pk))
start=(now+timedelta(days=1)).replace(hour=10,minute=0,second=0,microsecond=0)
barrier=Barrier(2)
def attempt(record):
 connections.close_all()
 h,u,v=record;h=Household.objects.get(pk=h);u=get_user_model().objects.get(pk=u)
 barrier.wait()
 try:
  book(h,u,dict(bay_id=ordinary.pk,vehicle_id=v,start=start.isoformat(),end=(start+timedelta(hours=1)).isoformat(),request_id='concurrent'))
  return 'success'
 except DomainError:return 'conflict'
 finally:connections.close_all()
with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(attempt,records))
assert sorted(result)==['conflict','success'],result
assert Reservation.objects.filter(bay=ordinary).count()==1
assert Reservation.objects.get(pk=old_pk).request_id=='preserve'
print('migration preserved; one success, one conflict')
'''
            result=subprocess.run([sys.executable,'-c',code],cwd=root,env=env,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('migration preserved; one success, one conflict',result.stdout)
