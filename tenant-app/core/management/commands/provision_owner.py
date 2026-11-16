import getpass
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand,CommandError
from django.core.validators import validate_email
from django.db import transaction
from core.models import Property,Household,Membership

class Command(BaseCommand):
    help='Trusted operator setup of a real household owner. No public apartment signup.'
    def add_arguments(self,p):
        p.add_argument('--property',type=int,required=True)
        p.add_argument('--apartment',required=True)
        p.add_argument('--household',required=True)
        p.add_argument('--username',required=True)
        p.add_argument('--email',required=True)
        p.add_argument('--name',required=True)
    def handle(self,*args,**o):
        if settings.DEMO_MODE:raise CommandError('Use a separate non-demo database and VOLTO_DEMO=0 for real residents.')
        User=get_user_model();email=o['email'].strip().lower()
        try:validate_email(email)
        except ValidationError:raise CommandError('Enter a valid email.')
        if User.objects.filter(username=o['username']).exists() or User.objects.filter(email__iexact=email).exists():raise CommandError('Account already exists. Do not overwrite credentials; use a trusted membership/invitation workflow.')
        user=User(username=o['username'],email=email,first_name=o['name'])
        password=getpass.getpass('Initial password (not echoed): ')
        if password!=getpass.getpass('Repeat password: '):raise CommandError('Passwords differ.')
        try:validate_password(password,user)
        except ValidationError as e:raise CommandError('; '.join(e.messages))
        with transaction.atomic():
            property=Property.objects.get(id=o['property'])
            if Household.objects.filter(property=property,apartment=o['apartment']).exists():raise CommandError('Apartment already provisioned; refuse to overwrite ownership.')
            h=Household(property=property,name=o['household'],apartment=o['apartment']);h.full_clean();h.save()
            user.set_password(password);user.full_clean();user.save()
            Membership.objects.create(household=h,user=user,role='owner')
        self.stdout.write(self.style.SUCCESS('Household owner provisioned. Deliver credentials privately; none were printed.'))
