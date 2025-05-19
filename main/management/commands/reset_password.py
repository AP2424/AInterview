from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Reset admin password for Render"

    def handle(self, *args, **options):
        User = get_user_model()
        admin = User.objects.filter(username='admin1').first()
        if admin:
            admin.set_password('P@ssword123$')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✅ Password updated.'))
        else:
            self.stdout.write(self.style.ERROR('❌ Admin user not found.'))