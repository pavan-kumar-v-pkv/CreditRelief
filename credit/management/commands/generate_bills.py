from django.core.management.base import BaseCommand
from credit.billing_utils import generate_billing_for_today

class Command(BaseCommand):
    help = 'Generate monthly billing for users'

    def handle(self, *args, **kwargs):
        generate_billing_for_today()
        self.stdout.write(self.style.SUCCESS('BILLING generate successfully for today'))