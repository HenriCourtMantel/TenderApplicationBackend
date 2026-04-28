from rest_framework import serializers
from .models import Location, Category, Company, Tender, Bid, BidDocument, CategoryCompany, CategoryTender, TenderStatusHistory, BidStatusHistory, Status, User, Currency, TenderAttachment

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

    def validate_number_of_employees(self, value):
        if value < 0:
            raise serializers.ValidationError("Number of employees cannot be negative")
        return value

    def validate_annual_revenue(self, value):
        if value < 0:
            raise serializers.ValidationError("Revenue cannot be negative")
        return value
    
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True, allow_blank=True)
    gender = serializers.CharField(required=True, allow_blank=True)
    cr_number = serializers.CharField(required=True, allow_blank=True)
    birth_date = serializers.DateField(required=True, allow_null=True)
    first_name = serializers.CharField(required=True, allow_blank=True)
    last_name = serializers.CharField(required=True, allow_blank=True)
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_cr_number(self, value):
        if value and len(value) < 5:
            raise serializers.ValidationError("CR number too short")
        return value

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

from django.utils import timezone

class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = '__all__'

    def validate(self, data):
        if data['budget_min'] > data['budget_max']:
            raise serializers.ValidationError("Min budget cannot exceed max budget")

        if data['deadline'] <= data['start_date']:
            raise serializers.ValidationError("Deadline must be after start date")

        if data['deadline'] <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future")

        return data
    
class TenderAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderAttachment
        fields = '__all__'

    def validate_size(self, value):
        if value <= 0:
            raise serializers.ValidationError("File size must be positive")
        return value
    
class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'

    def validate_total_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total price must be positive")
        return value

    def validate(self, data):
        tender = data.get('tender')
        if tender and tender.deadline < timezone.now():
            raise serializers.ValidationError("Cannot bid on expired tender")

        return data

class BidDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidDocument
        fields = '__all__'

    def validate_size(self, value):
        if value <= 0:
            raise serializers.ValidationError("File size must be positive")
        return value

class CategoryCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryCompany
        fields = '__all__'

    def validate(self, data):
        if CategoryCompany.objects.filter(
            category=data['category'],
            company=data['company']
        ).exists():
            raise serializers.ValidationError("This relation already exists")
        return data

class CategoryTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTender
        fields = '__all__'

    def validate(self, data):
        if CategoryTender.objects.filter(
            category=data['category'],
            tender=data['tender']
        ).exists():
            raise serializers.ValidationError("This relation already exists")
        return data

class TenderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderStatusHistory
        fields = '__all__'

class BidStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BidStatusHistory
        fields = '__all__'