from rest_framework import serializers
from .models import Evaluation, Location, Category, Company, SavedTender, Tender, Bid, BidDocument, CategoryCompany, CategoryTender, TenderStatusHistory, BidStatusHistory, Status, User, Currency, TenderAttachment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD 

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("No account found with this email.")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password.")

        if not user.is_active:
            raise AuthenticationFailed("This account is inactive.")

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

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
    email = serializers.EmailField(required=True)
    profile_picture = serializers.FileField(required=False, allow_null=True)
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
        if User.objects.filter(cr_number=value).exists():
            raise serializers.ValidationError("CR number already in use")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value
    
    def validate_phone(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError("Phone number too short")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already in use")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already in use")
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
    title = serializers.CharField(required=True, allow_blank=False)
    description = serializers.CharField(required=True, allow_blank=False)
    budget_min = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)
    budget_max = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)
    start_date = serializers.DateTimeField(required=True)
    deadline = serializers.DateTimeField(required=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all(), required=True)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), required=True)
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), required=True)
    class Meta:
        model = Tender
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        if data['budget_min'] > data['budget_max']:
            raise serializers.ValidationError("Min budget cannot exceed max budget")

        if data['deadline'] <= data['start_date']:
            raise serializers.ValidationError("Deadline must be after start date")

        if data['deadline'] <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future")

        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
class TenderAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderAttachment
        fields = '__all__'

    def validate_size(self, value):
        if value <= 0:
            raise serializers.ValidationError("File size must be positive")
        return value
    
class BidSerializer(serializers.ModelSerializer):
    proposal = serializers.CharField(required = True, allow_blank = False)
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), required=True)
    
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
        
class SavedTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedTender
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'