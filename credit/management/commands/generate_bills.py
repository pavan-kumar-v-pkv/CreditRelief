from django.core.management.base import BaseCommand
from credit.tasks import generate_billing_for_today

class Command(BaseCommand):
    help = 'Generate monthly billing for users'

    def handle(self, *args, **kwargs):
        generate_billing_for_today.delay()
        self.stdout.write(self.style.SUCCESS('BILLING generated successfully for today via Celery'))