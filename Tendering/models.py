from django.db import models
from django.contrib.auth.models import AbstractUser


class Location(models.Model):
    location_street = models.CharField('street name', max_length=100)
    location_city = models.CharField('city name', max_length=40)
    location_state = models.CharField('state name', max_length=40)

    def __str__(self):
        return f"{self.location_street}, {self.location_city}, {self.location_state}"

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
    profile_picture = models.FileField(upload_to='profile_pictures/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=False, blank=True)
    gender = models.CharField(max_length=10, null=False, blank=True)
    birth_date = models.DateField(null=False, blank=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    cr_number = models.CharField(max_length=100, blank=True, null=False, unique=True)

    def __str__(self):
        return self.email

class Currency(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.code

class TenderAttachment(models.Model):
    tender = models.ForeignKey('Tender', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='tender_attachments/')
    description = models.TextField(blank=True, null=True)
    size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Attachment for {self.tender.title}"

class Tender(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tenders")
    title = models.CharField(max_length=255)
    description = models.TextField()

    category= models.ForeignKey(Category, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateTimeField()
    deadline = models.DateTimeField()

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class BidDocument(models.Model):
    bid = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='bid_documents/')
    description = models.TextField(blank=True, null=True)
    size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)

    def __str__(self):
        return f"Bid Document {self.id}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="bids")

    creation_date = models.DateTimeField(auto_now_add=True)

    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    proposal = models.TextField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # cost_breakdown = models.TextField()

    def __str__(self):
        return f"Bid by {self.user.email} for {self.tender.title}"

class CategoryCompany(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('category', 'company')
    
    def __str__(self):
        return f"{self.company.company_name} - {self.category.name}"
    
class CategoryTender(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('category', 'tender')
    def __str__(self):
        return f"{self.tender.title} - {self.category.name}"
    
class TenderStatusHistory(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tender.title} - {self.status.name} at {self.changed_at}"
    
class BidStatusHistory(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.bid.user.email} for {self.bid.tender.title} - {self.status.name} at {self.changed_at}"