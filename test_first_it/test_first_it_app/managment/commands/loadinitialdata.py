from django.core.management.base import BaseCommand
from test_first_it_app.seeds import create_initial_data

class Command(BaseCommand):
    help = 'Loads initial data into the database'
    
    def handle(self, *args, **options):
        try:
            create_initial_data()
            self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error with loaded initial data: {str(e)}'))