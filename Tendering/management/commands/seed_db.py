import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Tendering.models import Field, Tender, User
from faker import Faker

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        User = get_user_model()
        
        # 1. Create Fields
        field_names = ['Construction', 'IT', 'Healthcare', 'Education', 'Logistics']
        fields = [Field.objects.get_or_create(name=name, description=fake.sentence())[0] for name in field_names]

        # 2. Ensure we have a user
        user, _ = User.objects.get_or_create(username='tester', email='test@test.com')
        user.set_password('password123')
        user.save()

        # 3. Create Tenders
        self.stdout.write("Generating Tenders...")
        for _ in range(20):
            tender = Tender.objects.create(
                user=user,
                title=f"{fake.job()} {fake.company()} Tender",
                description=fake.paragraph(),
                currency="USD",
                budget_min=random.randint(1000, 5000),
                budget_max=random.randint(6000, 20000),
                start_date=fake.date_this_year(),
                end_date=fake.future_date(),
                issuing_org=fake.company(),
                contact_info=fake.email(),
                location=fake.city(),
            )
            # Add random fields
            tender.fields.set(random.sample(fields, random.randint(1, 3)))
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded 20 tenders!'))