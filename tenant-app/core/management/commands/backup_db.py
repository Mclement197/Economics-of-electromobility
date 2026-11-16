import os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand,CommandError

class Command(BaseCommand):
    help='Consistent SQLite online backup outside the web root; backups contain private data.'
    def add_arguments(self,p):p.add_argument('--directory',required=True)
    def handle(self,*args,**o):
        destination=Path(o['directory']).resolve();destination.mkdir(parents=True,exist_ok=True,mode=0o700)
        root=Path(__file__).resolve().parents[4]
        if root==destination or root in destination.parents:raise CommandError('Choose a private backup folder outside the project repository.')
        source=Path(settings.DATABASES['default']['NAME']).resolve()
        target=destination/('voltoshare-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite3')
        with sqlite3.connect(source) as src,sqlite3.connect(target) as dst:
            src.backup(dst)
            if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise CommandError('Backup integrity check failed.')
        os.chmod(target,0o600)
        self.stdout.write(f'Backup complete: {target}')
