from django.db import models
from django.contrib.auth.models import AbstractUser


class Field(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class User(AbstractUser):
    phone = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    cr_number = models.CharField(max_length=100, blank=True, null=True)

    fields = models.ManyToManyField(Field, related_name="users")

    def __str__(self):
        return self.email


class Tender(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tenders")
    title = models.CharField(max_length=255)
    description = models.TextField()

    currency = models.CharField(max_length=10)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    issuing_org = models.CharField(max_length=255)
    contact_info = models.TextField()
    location = models.CharField(max_length=255)

    document_url = models.URLField(blank=True, null=True)  
    fields = models.ManyToManyField(Field, related_name="tenders")

    def __str__(self):
        return self.title


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="bids")

    creation_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=50)
    approval_status = models.CharField(max_length=50)

    description = models.TextField()
    document_url = models.URLField(blank=True, null=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_breakdown = models.TextField()

    def __str__(self):
        return f"Bid {self.id} - {self.tender.title}"


class SavedTender(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_tenders")
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="saved_by")

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tender')

    def __str__(self):
        return f"{self.user.email} saved {self.tender.title}"