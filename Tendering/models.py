from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random

class Location(models.Model):
    street = models.CharField('street name', max_length=100)
    city = models.CharField('city name', max_length=40)
    state = models.CharField('state name', max_length=40)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Company(models.Model):
    company_name = models.CharField("company name", max_length=40)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    cr_number = models.CharField("CR number", max_length=40)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    number_of_employees = models.IntegerField()
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.company_name


class Status(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20, null=False, blank=True)
    gender = models.CharField(max_length=10, null=False, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    cr_number = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        unique=True
    )

    is_verified = models.BooleanField(default=False)

    verification_document = models.FileField(
        upload_to='verification_docs/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.email


class Currency(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.code


class Tender(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tenders"
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    is_approved = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE
    )

    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    start_date = models.DateTimeField()

    deadline = models.DateTimeField()

    def default_completion_deadline():
      return timezone.now() + timedelta(days=90)

    completion_deadline = models.DateTimeField(
        default=default_completion_deadline
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title
    
class TenderAttachment(models.Model):
    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    file = models.FileField(
        upload_to='tender_attachments/'
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    size = models.PositiveIntegerField()

    content_type = models.CharField(max_length=100)

    def __str__(self):
        return f"Attachment for {self.tender.title}"


class Bid(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    creation_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)

    proposal = models.TextField()

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # NEW FIELDS
    execution_plan = models.TextField(
        null=True,
        blank=True
    )

    deliverables = models.TextField(
        null=True,
        blank=True
    )

    estimated_duration = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    company_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    contact_person = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    contact_email = models.EmailField(
        null=True,
        blank=True
    )

    contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Bid by {self.user.email} for {self.tender.title}"
    
class BidDocument(models.Model):
    bid = models.ForeignKey(
        Bid,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    file = models.FileField(
        upload_to='bid_documents/'
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    size = models.PositiveIntegerField()

    content_type = models.CharField(max_length=100)

    def __str__(self):
        return f"Bid Document {self.id}"


# NEW
class SavedTender(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tender')

    def __str__(self):
        return f"{self.user.email} saved {self.tender.title}"


# NEW
class Evaluation(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    comments = models.TextField()

    decision = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )

    evaluated_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.bid.title} - {self.decision}"


class CategoryCompany(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('category', 'company')

    def __str__(self):
        return f"{self.company.company_name} - {self.category.name}"


class CategoryTender(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('category', 'tender')

    def __str__(self):
        return f"{self.tender.title} - {self.category.name}"


class TenderStatusHistory(models.Model):
    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.tender.title} - {self.status.name}"


class BidStatusHistory(models.Model):
    bid = models.ForeignKey(
        Bid,
        on_delete=models.CASCADE
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Bid by {self.bid.user.email} for {self.bid.tender.title} - {self.status.name} at {self.changed_at}"
    



class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ('new_bid', 'New Bid'),
        ('bid_accepted', 'Bid Accepted'),
        ('bid_rejected', 'Bid Rejected'),
        ('tender_approved', 'Tender Approved'),
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    tender_title = models.CharField(max_length=255, default="title")
    bid_title = models.CharField(max_length=255, default="title")

    def __str__(self):
        return f"{self.recipient} - {self.notification_type}"


class OTP(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    code = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    is_verified = models.BooleanField(default=False)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"{self.user.email} - {self.code}"
    

class TenderPayment(models.Model):
    tender = models.OneToOneField(Tender, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("Visa", "Visa"),
            ("MasterCard", "MasterCard"),
            ("PayPal", "PayPal"),
        ],
        blank=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Paid", "Paid"),
        ],
        default="Pending"
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    payment_reference = models.CharField(
        max_length=100,
        blank=True
    )