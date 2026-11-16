"""Replaceable provider adapter. Mock data never claims physical charger control."""
from typing import Protocol
from django.conf import settings
from django.utils import timezone
from .models import Charger
from .services import DomainError, ingest_session


class ChargingProvider(Protocol):
    def statuses(self, property): ...
    def ingest(self, event): ...


class MockChargingProvider:
    def _check(self):
        if not settings.DEMO_MODE:
            raise DomainError('The mock provider is available only in explicitly enabled demo mode.')

    def statuses(self, property):
        self._check()
        return list(Charger.objects.filter(property=property).values('id','status','updated_at'))

    def ingest(self, event):
        self._check()
        return ingest_session(event)

    def set_status(self, charger, status):
        self._check()
        if status not in ('available','charging','offline','unknown'):
            raise DomainError('Unknown charger status.')
        charger.status,charger.updated_at=status,timezone.now()
        charger.save(update_fields=['status','updated_at'])
