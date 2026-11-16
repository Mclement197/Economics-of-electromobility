import json
from pathlib import Path
from django.core.management.base import BaseCommand,CommandError
from core.provider import MockChargingProvider
from core.services import DomainError

class Command(BaseCommand):
    help='Ingest a trusted JSON file with one event or event list via the demo-only mock provider.'
    def add_arguments(self,parser): parser.add_argument('file')
    def handle(self,*args,**options):
        try:
            payload=json.loads(Path(options['file']).read_text())
            events=payload if isinstance(payload,list) else [payload]
            for event in events:
                if not isinstance(event,dict): raise ValueError('Each event must be an object.')
                session=MockChargingProvider().ingest(event)
                self.stdout.write(f'{session.provider_event}: session {session.pk}, {session.status}, {session.cost_cents} cents')
        except (OSError,ValueError,DomainError) as error: raise CommandError(str(error))
