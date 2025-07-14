import ipaddress
from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Add an IP address to the BlockedIP model'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to block')

    def handle(self, *args, **options):
        ip_address = options['ip_address']

        # Validate IP address
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            self.stderr.write(self.style.ERROR(f"Invalid IP address: {ip_address}"))
            return

        # Check if IP is already blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            self.stderr.write(self.style.WARNING(f"IP address {ip_address} is already blocked"))
            return

        # Create and save BlockedIP instance
        try:
            BlockedIP.objects.create(ip_address=ip_address)
            self.stdout.write(self.style.SUCCESS(f"IP address {ip_address} blocked successfully"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error blocking IP address {ip_address}: {str(e)}"))