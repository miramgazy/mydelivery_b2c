from django.core.management.base import BaseCommand
from apps.organizations.models import Organization
from apps.iiko_integration.client import IikoClient
from apps.iiko_integration.services import TerminalSyncService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync terminal groups from iiko Cloud'

    def handle(self, *args, **options):
        organizations = Organization.objects.all()
        if not organizations:
            self.stdout.write(self.style.WARNING('No organizations found in database'))
            return

        sync_service = TerminalSyncService()

        for org in organizations:
            if not org.api_key:
                self.stdout.write(self.style.WARNING(f'No API key for organization {org.org_name}'))
                continue

            self.stdout.write(f'Syncing data for {org.org_name}...')
            
            try:
                client = IikoClient.from_organization(org)
                
                active_rms = list(org.rms_bases.filter(is_active=True))
                if active_rms:
                    for rms in active_rms:
                        self.stdout.write(f'Syncing RMS "{rms.name}" ({rms.iiko_organization_id})...')
                        # 1. Sync Terminal Groups for RMS
                        terminal_groups_data = client.get_terminal_groups([rms.iiko_organization_id])
                        synced_terminals = sync_service.sync_terminal_groups(terminal_groups_data, organization=org, rms_base=rms)
                        self.stdout.write(self.style.SUCCESS(f'  Synced {len(synced_terminals)} terminals for RMS {rms.name}'))

                        # 2. Sync Payment Types
                        payment_types_data = client.get_payment_types([rms.iiko_organization_id])
                        synced_payments = sync_service.sync_payment_types(org, payment_types_data)
                        self.stdout.write(self.style.SUCCESS(f'  Synced {len(synced_payments)} payment types for RMS {rms.name}'))
                elif org.iiko_organization_id:
                    # Fallback single RMS
                    terminal_groups_data = client.get_terminal_groups([org.iiko_organization_id])
                    synced_terminals = sync_service.sync_terminal_groups(terminal_groups_data, organization=org)
                    self.stdout.write(self.style.SUCCESS(f'Successfully synced {len(synced_terminals)} terminal groups for {org.org_name}'))

                    payment_types_data = client.get_payment_types([org.iiko_organization_id])
                    synced_payments = sync_service.sync_payment_types(org, payment_types_data)
                    self.stdout.write(self.style.SUCCESS(f'Successfully synced {len(synced_payments)} payment types for {org.org_name}'))
                else:
                    self.stdout.write(self.style.ERROR(f'No RMS bases or iiko_organization_id for {org.org_name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to sync for {org.org_name}: {str(e)}'))
