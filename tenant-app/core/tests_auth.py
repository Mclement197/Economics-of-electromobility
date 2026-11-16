"""Focused tenant boundary checks. All identities/data are fictional test fixtures."""
import hashlib
import io
import json
from datetime import timedelta
from urllib.parse import urlparse
from uuid import uuid4
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from .services import ingest_session, issue_invoice
from .models import (Membership, Household, Invitation, Vehicle, Reservation,
                     ChargingSession, Charger, Invoice)

User = get_user_model()
TEST_STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}


@override_settings(DEMO_MODE=True, AXES_ENABLED=False, STORAGES=TEST_STORAGES)
class HouseholdBoundaryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', stdout=io.StringIO())
        cls.alex = User.objects.get(username='alex')
        cls.sam = User.objects.get(username='sam')
        cls.jordan = User.objects.get(username='jordan')
        cls.home = Membership.objects.get(user=cls.alex).household
        cls.other = Membership.objects.get(user=cls.jordan).household
        cls.owner_membership = Membership.objects.get(user=cls.alex)
        cls.member_membership = Membership.objects.get(user=cls.sam)
        cls.foreign_membership = Membership.objects.get(user=cls.jordan)
        cls.car = Vehicle.objects.filter(household=cls.home, archived=False).first()
        cls.foreign_car = Vehicle.objects.get(household=cls.other)
        cls.charger = Charger.objects.filter(property=cls.home.property, status='available').first()
        # Seed a genuine foreign invoice/session so scoped exports cannot pass vacuously.
        prior=(timezone.now()-timedelta(days=35)).replace(hour=9,minute=0,second=0,microsecond=0)
        foreign_session=ingest_session({'provider_event':'auth-foreign-private-session','vehicle_id':cls.foreign_car.id,'charger_id':cls.charger.id,'start':prior.isoformat(),'end':(prior+timedelta(hours=1)).isoformat(),'energy_kwh':'12.125'})
        issue_invoice(cls.other,foreign_session.end.astimezone(ZoneInfo(cls.home.property.timezone)).strftime('%Y-%m'))

    def setUp(self):
        self.client.force_login(self.alex, backend='django.contrib.auth.backends.ModelBackend')

    def post(self, path, payload=None, client=None):
        return (client or self.client).post(path, data=json.dumps(payload or {}), content_type='application/json')

    def book_payload(self, vehicle=None, days=5):
        start=(timezone.now()+timedelta(days=days)).replace(hour=10, minute=0, second=0, microsecond=0)
        return {'charger_id':self.charger.id, 'vehicle_id':(vehicle or self.car).id,
                'start':start.isoformat(), 'end':(start+timedelta(hours=1)).isoformat(),
                'request_id':str(uuid4())}

    def invite(self, email='guest@example.test'):
        response=self.post('/api/invitations/', {'email':email})
        self.assertEqual(response.status_code, 200, response.content)
        path=urlparse(response.json()['url']).path
        token=path.strip('/').split('/')[-1]
        invitation=Invitation.objects.get(token_hash=hashlib.sha256(token.encode()).hexdigest())
        return path, token, invitation

    def test_anonymous_private_routes_require_authentication(self):
        anon=Client()
        invoice=Invoice.objects.filter(household=self.home).first()
        for path in ['/api/state/', '/api/history.csv', f'/invoices/{invoice.id}/print/']:
            with self.subTest(path=path):
                response=anon.get(path)
                self.assertEqual(response.status_code,401)
                self.assertFalse(response.json()['ok'])
        self.assertEqual(self.post('/api/vehicles/', {'name':'Not saved'}, anon).status_code,401)

    def test_state_is_household_scoped_and_foreign_occupancy_is_anonymous(self):
        response=self.client.get('/api/state/?household_id='+str(self.other.id))
        self.assertEqual(response.status_code,200,response.content)
        state=response.json()
        self.assertEqual(state['household']['id'],self.home.id)
        self.assertTrue(all(v['id']!=self.foreign_car.id for v in state['vehicles']))
        self.assertTrue(all(m['user_id']!=self.jordan.id for m in state['members']))
        foreign_ids=set(Reservation.objects.filter(household=self.other).values_list('id',flat=True))
        self.assertFalse(any(r['id'] in foreign_ids for r in state['reservations']))
        foreign_occupancy=[o for o in state['occupancy'] if not o['own']]
        self.assertTrue(foreign_occupancy)
        for occupied in foreign_occupancy:
            self.assertEqual(set(occupied),{'charger_id','start','end','kind','own'} | ({'estimated'} if occupied['kind']=='session' else set()))
        body=response.content.decode()
        for secret in [self.other.name, self.foreign_car.plate, self.jordan.email]:
            self.assertNotIn(secret,body)
        self.assertIn('no-store',response['Cache-Control'])

    def test_direct_foreign_records_mutations_and_exports_are_rejected(self):
        foreign_reservation=Reservation.objects.filter(household=self.other).first()
        foreign_invoice=Invoice.objects.filter(household=self.other).first()
        self.assertIsNotNone(foreign_invoice)
        original=(foreign_reservation.start,foreign_reservation.end,foreign_reservation.status)
        attempts=[
            (f'/api/vehicles/{self.foreign_car.id}/change/',{'name':'Stolen','plate':'BAD','connector':'Type 2'}),
            (f'/api/vehicles/{self.foreign_car.id}/archive/',{}),
            (f'/api/reservations/{foreign_reservation.id}/change/',self.book_payload()),
            (f'/api/reservations/{foreign_reservation.id}/cancel/',{}),
            ('/api/reservations/',self.book_payload(self.foreign_car)),
            (f'/api/members/{self.foreign_membership.id}/remove/',{}),
        ]
        for path,payload in attempts:
            with self.subTest(path=path):
                self.assertIn(self.post(path,payload).status_code,[403,404,409])
        foreign_reservation.refresh_from_db()
        self.assertEqual((foreign_reservation.start,foreign_reservation.end,foreign_reservation.status),original)
        self.foreign_car.refresh_from_db();self.assertFalse(self.foreign_car.archived)
        self.assertEqual(self.client.get(f'/invoices/{foreign_invoice.id}/print/').status_code,404)
        csv=self.client.get('/api/history.csv?vehicle='+str(self.foreign_car.id))
        self.assertEqual(csv.status_code,200)
        self.assertEqual(len(csv.content.decode().splitlines()),1)
        self.assertNotIn(self.foreign_car.name,self.client.get('/api/history.csv').content.decode())

    def test_member_has_shared_read_access_and_vehicle_booking_permissions_only(self):
        self.client.force_login(self.sam,backend='django.contrib.auth.backends.ModelBackend')
        state=self.client.get('/api/state/').json()
        self.assertEqual(state['role'],'member')
        self.assertTrue(state['sessions']);self.assertTrue(state['invoices'])
        self.assertEqual(state['invitations'],[])
        for path,payload in [('/api/invitations/',{'email':'blocked@example.test'}),('/api/household/',{'name':'Unapproved'}),(f'/api/members/{self.owner_membership.id}/remove/',{})]:
            with self.subTest(path=path):self.assertIn(self.post(path,payload).status_code,[403,409])
        response=self.post('/api/vehicles/',{'name':'Member car','plate':'TEST-MEMBER','driver_id':self.sam.id,'connector':'Type 2','battery_kwh':'52.50','make_model':'Fictional'})
        self.assertEqual(response.status_code,200,response.content)
        vehicle=Vehicle.objects.get(id=response.json()['vehicle_id'])
        self.assertEqual(vehicle.household_id,self.home.id)
        count=ChargingSession.objects.count()
        booking=self.post('/api/reservations/',self.book_payload(vehicle))
        self.assertEqual(booking.status_code,200,booking.content)
        rid=booking.json()['reservation_id']
        change=self.post(f'/api/reservations/{rid}/change/',self.book_payload(vehicle,days=6))
        self.assertEqual(change.status_code,200,change.content)
        self.assertEqual(self.post(f'/api/reservations/{rid}/cancel/').status_code,200)
        self.assertEqual(ChargingSession.objects.count(),count)
        self.assertEqual(self.post(f'/api/vehicles/{vehicle.id}/archive/').status_code,200)
        invoice=Invoice.objects.filter(household=self.home).first()
        self.assertEqual(self.client.get(f'/invoices/{invoice.id}/print/').status_code,200)

    def test_client_supplied_household_and_foreign_driver_cannot_claim_records(self):
        response=self.post('/api/vehicles/',{'name':'Scoped','plate':'TEST-SCOPE','connector':'Type 2','household_id':self.other.id,'driver_id':self.jordan.id})
        self.assertEqual(response.status_code,404)
        self.assertFalse(Vehicle.objects.filter(plate='TEST-SCOPE').exists())
        response=self.post('/api/vehicles/',{'name':'Scoped','plate':'TEST-SCOPE','connector':'Type 2','household_id':self.other.id})
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(Vehicle.objects.get(pk=response.json()['vehicle_id']).household_id,self.home.id)

    def test_removal_revokes_existing_session_access_and_stale_invitation(self):
        member=Client();member.force_login(self.sam,backend='django.contrib.auth.backends.ModelBackend')
        self.assertEqual(member.get('/api/state/').status_code,200)
        # Outstanding second links must not let a removed member immediately return.
        invitation=Invitation.objects.create(household=self.home,email=self.sam.email,token_hash=hashlib.sha256(b'stale-member-link').hexdigest(),expires_at=timezone.now()+timedelta(hours=24))
        response=self.post(f'/api/members/{self.member_membership.id}/remove/')
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(member.get('/api/state/').status_code,403)
        self.assertEqual(member.get('/api/history.csv').status_code,403)
        invoice=Invoice.objects.filter(household=self.home).first()
        self.assertEqual(member.get(f'/invoices/{invoice.id}/print/').status_code,403)
        self.assertEqual(self.post('/api/reservations/',self.book_payload(),member).status_code,403)
        invitation.refresh_from_db();self.assertTrue(invitation.revoked)
        self.assertEqual(member.post('/invite/stale-member-link/').status_code,410)

    def test_last_owner_cannot_be_removed(self):
        response=self.post(f'/api/members/{self.owner_membership.id}/remove/')
        self.assertIn(response.status_code,[403,409])
        self.owner_membership.refresh_from_db();self.assertTrue(self.owner_membership.active)

    def test_invitation_is_hashed_email_bound_and_single_use(self):
        user=User.objects.create_user('acceptedguest',email='accepted@example.test')
        path,token,invitation=self.invite(user.email)
        self.assertNotEqual(invitation.token_hash,token)
        self.assertEqual(invitation.token_hash,hashlib.sha256(token.encode()).hexdigest())
        state=self.client.get('/api/state/').json()
        self.assertNotIn(token,json.dumps(state))
        wrong=Client();wrong.force_login(self.jordan,backend='django.contrib.auth.backends.ModelBackend')
        self.assertEqual(wrong.post(path).status_code,200)
        self.assertFalse(Membership.objects.filter(user=self.jordan,household=self.home).exists())
        invitation.refresh_from_db();self.assertIsNone(invitation.used_at)
        guest=Client();guest.force_login(user,backend='django.contrib.auth.backends.ModelBackend')
        self.assertEqual(guest.post(path).status_code,302)
        membership=Membership.objects.get(user=user,household=self.home)
        self.assertEqual(membership.role,'member');self.assertTrue(membership.active)
        self.assertEqual(guest.get('/api/state/').json()['household']['id'],self.home.id)
        self.assertEqual(guest.post(path).status_code,410)

    def test_expired_revoked_and_foreign_invites_are_rejected(self):
        path,token,invitation=self.invite()
        other=Client();other.force_login(self.jordan,backend='django.contrib.auth.backends.ModelBackend')
        self.assertEqual(self.post(f'/api/invitations/{invitation.id}/revoke/',client=other).status_code,404)
        invitation.expires_at=timezone.now()-timedelta(seconds=1);invitation.save(update_fields=['expires_at'])
        self.assertEqual(Client().get(path).status_code,410)
        path2,_,invitation2=self.invite('another@example.test')
        self.assertEqual(self.post(f'/api/invitations/{invitation2.id}/revoke/').status_code,200)
        self.assertEqual(Client().get(path2).status_code,410)
        self.assertEqual(Client().get('/invite/unknown-token/').status_code,410)

    def test_registration_requires_valid_invite_and_cannot_choose_household_or_role(self):
        path,_,invitation=self.invite('newrelative@example.test')
        guest=Client()
        response=guest.post(path,{'name':'Fictional Relative','username':'newrelative','password1':'Fictional-test-only-4638!','password2':'Fictional-test-only-4638!','email':'not-the-invited@example.test','household_id':self.other.id,'role':'owner'})
        self.assertEqual(response.status_code,302,response.content)
        user=User.objects.get(username='newrelative')
        self.assertEqual(user.email,invitation.email)
        self.assertTrue(user.has_usable_password())
        self.assertEqual(Membership.objects.get(user=user).household_id,self.home.id)
        self.assertEqual(Membership.objects.get(user=user).role,'member')
        self.assertEqual(guest.get('/signup/').status_code,404)
        self.assertEqual(guest.post('/api/signup/',{'household_id':self.other.id}).status_code,404)
        self.assertEqual(guest.post('/invite/no-valid-token/',{'username':'uninvited'}).status_code,410)
        self.assertFalse(User.objects.filter(username='uninvited').exists())

    def test_csrf_is_required_on_login_logout_and_state_changes(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/login/demo/',{'persona':'alex'}).status_code,403)
        client.force_login(self.alex,backend='django.contrib.auth.backends.ModelBackend')
        self.assertEqual(client.post('/api/household/',data=json.dumps({'name':'not allowed'}),content_type='application/json').status_code,403)
        self.assertEqual(client.post('/logout/').status_code,403)
        self.assertEqual(client.get('/api/state/').status_code,200)
        csrf=client.cookies['csrftoken'].value
        good=client.post('/api/household/',data=json.dumps({'name':'Test home'}),content_type='application/json',HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(good.status_code,200,good.content)
        self.assertEqual(client.get('/logout/').status_code,405)

    def test_invoice_payment_reset_and_ingest_have_no_tenant_endpoint(self):
        invoice=Invoice.objects.filter(household=self.home,status='unpaid').first()
        for path in [f'/api/invoices/{invoice.id}/pay/',f'/api/invoices/{invoice.id}/paid/','/api/reset/','/api/seed/','/api/ingest/','/api/invoices/issue/']:
            with self.subTest(path=path):self.assertEqual(self.post(path,{'status':'paid'}).status_code,404)
        invoice.refresh_from_db();self.assertEqual(invoice.status,'unpaid')

    @override_settings(DEMO_MODE=False)
    def test_production_defaults_disable_demo_persona_entry(self):
        anonymous=Client()
        self.assertEqual(anonymous.post('/login/demo/',{'persona':'alex'}).status_code,404)
        self.assertNotIn('Explore as Alex',anonymous.get('/login/').content.decode())
        self.assertEqual(anonymous.post('/api/reset/').status_code,404)

    def test_demo_entry_cannot_impersonate_a_password_account_or_redirect_offsite(self):
        self.alex.set_password('Fictional-test-only-4826!');self.alex.save(update_fields=['password'])
        anonymous=Client()
        self.assertEqual(anonymous.post('/login/demo/',{'persona':'alex'}).status_code,403)
        response=anonymous.post('/login/demo/',{'persona':'sam','next':'https://attacker.invalid/'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(response['Location'],'/')
