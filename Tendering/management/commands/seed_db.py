import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from datetime import timedelta
from Tendering.models import (
    Location, Category, Company, Status, User, 
    Currency, Tender, Bid
)

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with fake data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        status_names = ['Open', 'Closed', 'Pending', 'Awarded', 'Cancelled']
        statuses = [Status.objects.get_or_create(name=name, defaults={'description': fake.sentence()})[0] for name in status_names]

        category_names = ['Construction', 'IT Services', 'Healthcare', 'Consulting', 'Logistics']
        categories = [Category.objects.get_or_create(name=name, defaults={'description': fake.sentence()})[0] for name in category_names]

        currency_data = [('USD', 'US Dollar'), ('SAR', 'Saudi Riyal'), ('EUR', 'Euro')]
        currencies = [Currency.objects.get_or_create(code=code, defaults={'name': name})[0] for code, name in currency_data]

        locations = []
        for _ in range(10):
            loc = Location.objects.create(
                street=fake.street_address(),
                city=fake.city(),
                state=fake.state()
            )
            locations.append(loc)

        companies = []
        for _ in range(5):
            comp = Company.objects.create(
                company_name=fake.company(),
                location=random.choice(locations),
                cr_number=fake.unique.numerify(text='##########'),
                category=random.choice(categories),
                number_of_employees=random.randint(10, 500),
                annual_revenue=random.randint(100000, 1000000)
            )
            companies.append(comp)

        users = []
        for _ in range(5):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='password123',
                phone=fake.numerify(text='##########'),
                gender=random.choice(['Male', 'Female']),
                birth_date=fake.date_of_birth(minimum_age=25, maximum_age=60),
                company=random.choice(companies),
                cr_number=fake.unique.numerify(text='##########')
            )
            users.append(user)

        tenders = []
        for _ in range(10):
            start = timezone.now() + timedelta(days=random.randint(-5, 5))
            tender = Tender.objects.create(
                user=random.choice(users),
                title=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=5),
                category=random.choice(categories),
                currency=random.choice(currencies),
                budget_min=random.randint(1000, 5000),
                budget_max=random.randint(6000, 20000),
                start_date=start,
                deadline=start + timedelta(days=random.randint(10, 30)),
                location=random.choice(locations),
                status=random.choice(statuses)
            )
            tenders.append(tender)

        for _ in range(15):
            Bid.objects.create(
                user=random.choice(users),
                tender=random.choice(tenders),
                status=random.choice(statuses),
                title=f"Bid for {fake.word()}",
                proposal=fake.text(),
                total_price=random.randint(5000, 15000)
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Tendering database!'))