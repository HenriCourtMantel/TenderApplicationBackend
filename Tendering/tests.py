from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from .models import Category, Currency, Location, Status, Tender, TenderPayment, User
from .views import TenderPaymentView, TenderViewSet


class TenderPaymentFlowTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='password123',
            is_verified=True,
            cr_number='CR-OWNER-1',
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            is_verified=True,
            is_staff=True,
            cr_number='CR-ADMIN-1',
        )
        self.category = Category.objects.create(name='IT', description='Tech')
        self.currency = Currency.objects.create(code='USD', name='US Dollar')
        self.location = Location.objects.create(street='123', city='Nairobi', state='Nairobi')
        self.status = Status.objects.create(name='Open', description='Open for bids')

        self.tender = Tender.objects.create(
            user=self.owner,
            title='Website Development',
            description='Build a website',
            is_approved=False,
            category=self.category,
            currency=self.currency,
            budget_min=1000,
            budget_max=5000,
            start_date=timezone.now() + timedelta(days=1),
            deadline=timezone.now() + timedelta(days=10),
            completion_deadline=timezone.now() + timedelta(days=90),
            location=self.location,
            status=self.status,
        )

    def test_admin_approval_creates_pending_payment_and_keeps_tender_private(self):
        request = self.factory.post(f'/tenders/{self.tender.pk}/approve/')
        force_authenticate(request, user=self.admin)

        response = TenderViewSet.as_view({'post': 'approve'})(request, pk=self.tender.pk)

        self.tender.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.tender.is_approved)
        self.assertTrue(TenderPayment.objects.filter(tender=self.tender, payment_status='Pending').exists())

    def test_payment_view_makes_tender_public_when_paid(self):
        TenderPayment.objects.create(tender=self.tender, amount=100.00, payment_status='Pending')

        request = self.factory.post(
            f'/tenders/{self.tender.pk}/pay/',
            {'payment_method': 'Visa', 'payment_reference': 'ref-123'},
            format='json',
        )
        force_authenticate(request, user=self.owner)

        response = TenderPaymentView.as_view()(request, tender_id=self.tender.pk)

        self.tender.refresh_from_db()
        payment = TenderPayment.objects.get(tender=self.tender)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.tender.is_approved)
        self.assertEqual(payment.payment_status, 'Paid')
