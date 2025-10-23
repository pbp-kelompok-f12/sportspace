from django.core.management.base import BaseCommand
from booking.models import Venue

class Command(BaseCommand):
    help = 'Create sample venues for testing'

    def handle(self, *args, **options):
        venues_data = [
            {
                'name': 'Simply Padel',
                'location': 'Senopati',
                'address': 'Jl. Senopati Raya No. 88, Jakarta Selatan',
                'latitude': -6.2088,
                'longitude': 106.8456,
                'description': 'Premium padel court with modern facilities'
            },
            {
                'name': 'Padel Center Jakarta',
                'location': 'Kemang',
                'address': 'Jl. Kemang Raya No. 12, Jakarta Selatan',
                'latitude': -6.2615,
                'longitude': 106.8106,
                'description': 'Professional padel courts with coaching services'
            },
            {
                'name': 'Sport Hub Padel',
                'location': 'SCBD',
                'address': 'Jl. Sudirman No. 52-53, Jakarta Selatan',
                'latitude': -6.2250,
                'longitude': 106.8000,
                'description': 'Luxury padel courts in the heart of Jakarta'
            }
        ]

        for venue_data in venues_data:
            venue, created = Venue.objects.get_or_create(
                name=venue_data['name'],
                defaults=venue_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created venue: {venue.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Venue already exists: {venue.name}')
                )
