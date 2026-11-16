from django.core.management.base import BaseCommand, CommandError
from core.models import Household
from core.services import DomainError, issue_invoice

class Command(BaseCommand):
    help='Issue immutable invoices for a completed YYYY-MM, once per household. No tenant endpoint.'
    def add_arguments(self,parser):
        parser.add_argument('period')
        parser.add_argument('--household',type=int)
    def handle(self,*args,**options):
        households=Household.objects.all()
        if options['household'] is not None:
            households=households.filter(pk=options['household'])
            if not households.exists(): raise CommandError('Household not found.')
        try:
            for household in households:
                invoice=issue_invoice(household,options['period'])
                self.stdout.write(f'{household.pk}: {invoice.number if invoice else "No unbilled completed sessions"}')
        except DomainError as error: raise CommandError(str(error))
