import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
from Tendering.models import (
    User, Company, Location, Category, Status, Currency, Tender, Bid
)

class Command(BaseCommand):
    help = 'Seeds the database with initial dummy data for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write(self.style.WARNING('Clearing old data...'))
        Bid.objects.all().delete()
        Tender.objects.all().delete()
        Company.objects.all().delete()
        Location.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.SUCCESS('Seeding Statuses, Categories, and Currencies...'))
        
        status_names = ['Open', 'Closed', 'Pending', 'Awarded', 'Rejected']
        statuses = {}
        for name in status_names:
            status, _ = Status.objects.get_or_create(name=name, defaults={'description': f'Tender/Bid is {name}'})
            statuses[name] = status

        category_names = ['Construction', 'IT & Software', 'Healthcare', 'Logistics', 'Marketing']
        categories = []
        for name in category_names:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': f'All {name} related tenders'})
            categories.append(cat)

        currency_data = [('USD', 'US Dollar'), ('EUR', 'Euro'), ('AED', 'UAE Dirham'), ('SAR', 'Saudi Riyal')]
        currencies = []
        for code, name in currency_data:
            curr, _ = Currency.objects.get_or_create(code=code, defaults={'name': name})
            currencies.append(curr)

        self.stdout.write(self.style.SUCCESS('Seeding Users and Companies...'))
        users = []
        for i in range(15):
            loc = Location.objects.create(
                street=fake.street_address(),
                city=fake.city(),
                state=fake.state()
            )
            
            comp = Company.objects.create(
                company_name=fake.company(),
                location=loc,
                cr_number=fake.unique.numerify(text='CR-#########'),
                category=random.choice(categories),
                number_of_employees=random.randint(5, 500),
                annual_revenue=round(random.uniform(50000, 5000000), 2)
            )

            email = fake.unique.email()
            user = User.objects.create(
                username=email.split('@')[0] + str(random.randint(100, 999)), # Ensure unique username
                email=email,
                password=make_password('password123'), # Default password for all seed users
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number()[:20],
                gender=random.choice(['Male', 'Female']),
                birth_date=fake.date_of_birth(minimum_age=25, maximum_age=60),
                company=comp,
                cr_number=fake.unique.numerify(text='USER-CR-#######'),
                is_verified=True, # Verified so they can participate
                is_active=True
            )
            users.append(user)

        self.stdout.write(self.style.SUCCESS('Seeding Tenders...'))
        tenders = []
        for i in range(20):
            budget_min = round(random.uniform(1000, 50000), 2)
            budget_max = budget_min + round(random.uniform(5000, 50000), 2)
            
            start_date = timezone.now() - timedelta(days=random.randint(0, 10))
            deadline = timezone.now() + timedelta(days=random.randint(5, 30))
            completion_deadline = deadline + timedelta(days=random.randint(30, 180))

            tender = Tender.objects.create(
                user=random.choice(users),
                title=fake.catch_phrase(),
                description=fake.text(max_nb_chars=500),
                is_approved=random.choice([True, True, True, False]), # 75% chance to be approved
                category=random.choice(categories),
                currency=random.choice(currencies),
                budget_min=budget_min,
                budget_max=budget_max,
                start_date=start_date,
                deadline=deadline,
                completion_deadline=completion_deadline,
                location=random.choice(Location.objects.all()),
                status=statuses['Open'] # Default to Open
            )
            tenders.append(tender)

        self.stdout.write(self.style.SUCCESS('Seeding Bids...'))
        for tender in tenders:
            if not tender.is_approved:
                continue
                
            num_bids = random.randint(1, 5)
            
            eligible_users = [u for u in users if u != tender.user]
            bidding_users = random.sample(eligible_users, min(num_bids, len(eligible_users)))

            for bidder in bidding_users:
                Bid.objects.create(
                    user=bidder,
                    tender=tender,
                    status=statuses['Pending'],
                    title=f"Proposal for {tender.title[:20]}...",
                    proposal=fake.text(max_nb_chars=800),
                    total_price=round(random.uniform(float(tender.budget_min), float(tender.budget_max)), 2),
                    execution_plan="Phase 1: Setup\nPhase 2: Execution\nPhase 3: Delivery",
                    deliverables="1. Source code\n2. Documentation",
                    estimated_duration=f"{random.randint(1, 12)} months",
                    company_name=bidder.company.company_name,
                    contact_person=f"{bidder.first_name} {bidder.last_name}",
                    contact_email=bidder.email,
                    contact_phone=bidder.phone
                )

        self.stdout.write(self.style.SUCCESS('Database successfully seeded!'))
        self.stdout.write(self.style.WARNING('NOTE: All seed user passwords are set to: password123'))