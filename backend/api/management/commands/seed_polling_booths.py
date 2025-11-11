"""
Management command to seed sample polling booth data for testing
"""
from django.core.management.base import BaseCommand
from api.models import State, District, Constituency, PollingBooth


class Command(BaseCommand):
    help = 'Seeds sample polling booth data for major constituencies'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Seeding polling booth data...'))

        try:
            tn = State.objects.get(code='TN')
        except State.DoesNotExist:
            self.stdout.write(self.style.ERROR('Tamil Nadu state not found. Run seed_political_data first.'))
            return

        # Sample booth data for major constituencies
        booth_data = {
            'Chennai': {
                'Anna Nagar': [
                    ('001', 'Anna Nagar East Primary School', 'Anna Nagar East, 2nd Avenue'),
                    ('002', 'Anna Nagar West Corporation School', 'Anna Nagar West, 5th Avenue'),
                    ('003', 'Shanti Colony Government School', 'Shanti Colony Main Road'),
                    ('004', 'Mogappair Elementary School', 'Mogappair East'),
                    ('005', 'Thirumangalam High School', 'Thirumangalam West'),
                    ('006', 'SBOA School', 'Anna Nagar, 3rd Avenue'),
                    ('007', 'Sacred Heart School', 'Anna Nagar, 6th Avenue'),
                    ('008', 'Corporation Middle School', 'Mogappair West'),
                    ('009', 'Government High School', 'Padi Junction'),
                    ('010', 'Municipal Elementary School', 'Ambattur Estate'),
                ],
                'T. Nagar': [
                    ('001', 'T. Nagar Corporation School', 'T. Nagar, Pondy Bazaar'),
                    ('002', 'Panagal Park Elementary School', 'Panagal Park'),
                    ('003', 'Thyagaraya Nagar High School', 'T. Nagar Main Road'),
                    ('004', 'Nandanam Government School', 'Nandanam Arts College Road'),
                    ('005', 'Teynampet Corporation School', 'Teynampet'),
                    ('006', 'Alwarpet Elementary School', 'Alwarpet'),
                    ('007', 'Mandaveli High School', 'Mandaveli'),
                    ('008', 'CIT Nagar Corporation School', 'CIT Nagar'),
                ],
                'Mylapore': [
                    ('001', 'Mylapore Corporation School', 'Mylapore Tank Road'),
                    ('002', 'Mandaveli Elementary School', 'Mandaveli Main Road'),
                    ('003', 'San Thome High School', 'San Thome Beach Road'),
                    ('004', 'Luz Church Road School', 'Luz Church Road'),
                    ('005', 'R.A. Puram Government School', 'R.A. Puram'),
                ],
            },
            'Coimbatore': {
                'Coimbatore North': [
                    ('001', 'RS Puram Corporation School', 'RS Puram'),
                    ('002', 'Gandhipuram Elementary School', 'Gandhipuram'),
                    ('003', 'Town Hall Corporation School', 'Town Hall Area'),
                    ('004', 'Sidhapudur Government School', 'Sidhapudur'),
                    ('005', 'Ram Nagar Corporation School', 'Ram Nagar'),
                ],
                'Coimbatore South': [
                    ('001', 'Peelamedu Government School', 'Peelamedu'),
                    ('002', 'Singanallur Corporation School', 'Singanallur'),
                    ('003', 'Saibaba Colony Elementary School', 'Saibaba Colony'),
                    ('004', 'Thudiyalur Government School', 'Thudiyalur'),
                    ('005', 'Vilankurichi Corporation School', 'Vilankurichi'),
                ],
            },
            'Madurai': {
                'Madurai Central': [
                    ('001', 'Meenakshi Temple Area School', 'Near Meenakshi Temple'),
                    ('002', 'Tallakulam Corporation School', 'Tallakulam'),
                    ('003', 'Vilakkuthoon Elementary School', 'Vilakkuthoon'),
                    ('004', 'Periyar Bus Stand School', 'Periyar Bus Stand Area'),
                    ('005', 'Anna Nagar Corporation School', 'Madurai Anna Nagar'),
                ],
                'Madurai North': [
                    ('001', 'Bypass Road Government School', 'Bypass Road'),
                    ('002', 'Thirunagar Corporation School', 'Thirunagar'),
                    ('003', 'KK Nagar Elementary School', 'KK Nagar'),
                    ('004', 'Arapalayam Government School', 'Arapalayam'),
                ],
            },
            'Salem': {
                'Salem (North)': [
                    ('001', 'Cherry Road Corporation School', 'Cherry Road'),
                    ('002', 'Fairlands Elementary School', 'Fairlands'),
                    ('003', 'Suramangalam Government School', 'Suramangalam'),
                    ('004', 'Hasthampatti Corporation School', 'Hasthampatti'),
                ],
                'Salem (South)': [
                    ('001', 'Ammapet Corporation School', 'Ammapet'),
                    ('002', 'Swarnapuri Elementary School', 'Swarnapuri'),
                    ('003', 'Meyyanur Government School', 'Meyyanur'),
                ],
            },
        }

        created_count = 0
        skipped_count = 0

        for district_name, constituencies in booth_data.items():
            try:
                district = District.objects.get(name=district_name, state=tn)

                for constituency_name, booths in constituencies.items():
                    try:
                        constituency = Constituency.objects.get(
                            name=constituency_name,
                            district=district,
                            state=tn
                        )

                        for booth_number, building_name, area in booths:
                            booth, created = PollingBooth.objects.get_or_create(
                                constituency=constituency,
                                booth_number=booth_number,
                                defaults={
                                    'state': tn,
                                    'district': district,
                                    'name': f'{building_name}',
                                    'building_name': building_name,
                                    'area': area,
                                    'total_voters': 800 + (int(booth_number) * 50),  # Sample voter count
                                    'is_active': True,
                                }
                            )

                            if created:
                                created_count += 1
                                self.stdout.write(
                                    f'  Created: {constituency_name} - Booth {booth_number}'
                                )
                            else:
                                skipped_count += 1

                    except Constituency.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  Constituency not found: {constituency_name} in {district_name}'
                            )
                        )

            except District.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'District not found: {district_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Polling booth seeding complete!'
                f'\n  Created: {created_count} booths'
                f'\n  Skipped: {skipped_count} (already exist)'
            )
        )
