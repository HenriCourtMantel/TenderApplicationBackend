import re

from rest_framework import serializers
from .models import Location, Category, Company, Tender, Bid, BidDocument, CategoryCompany, CategoryTender, TenderStatusHistory, BidStatusHistory, Status, User, Currency, TenderAttachment, Notification, OTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q
from .models import *
from django.utils import timezone
from django.db import transaction

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD  # tells Simple JWT to use email

    def validate(self, attrs):
        identifier = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(
                Q(email=identifier) |
                Q(phone=identifier)
            )

        except User.DoesNotExist:
            raise AuthenticationFailed(
                "No account found."
            )

        if not user.check_password(password):
            raise AuthenticationFailed(
                "Incorrect password."
            )

        if not user.is_active:
            raise AuthenticationFailed(
                "This account is inactive."
            )

        if not user.is_verified:
            raise AuthenticationFailed(
                "Your account is pending admin approval."
            )

        refresh = self.get_token(user)

        return {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "is_verified": user.is_verified,
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


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

def validate_username(value):
    if value.isdigit():
        raise serializers.ValidationError("Username cannot be only numbers.")
    if not re.search(r'[a-zA-Z]', value):
        raise serializers.ValidationError("Username must contain at least one letter.")
    return value

class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    category_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'gender', 'birth_date', 'cr_number', 
            'first_name', 'last_name', 'password', 'username',
            'company_name', 'category_name', 'is_verified'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'validators': [validate_username]},
        }
        read_only_fields = ['is_verified']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.company:
            representation['company_name'] = instance.company.company_name
            if instance.company.category:
                representation['category_name'] = instance.company.category.name
            else:
                representation['category_name'] = None
        else:
            representation['company_name'] = None
            representation['category_name'] = None      
        return representation

    @transaction.atomic 
    def create(self, validated_data):
        company_name = validated_data.pop('company_name', None)
        category_name = validated_data.pop('category_name', None)
        cr_number = validated_data.get('cr_number', '')
        password = validated_data.pop('password')

        company_instance = None

        if company_name and category_name:
            location, _ = Location.objects.get_or_create(
                street="Pending", 
                city="Pending", 
                state="Pending"
            )
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'{category_name} category'}
            )
            
            company_instance = Company.objects.create(
                company_name=company_name,
                location=location,
                cr_number=cr_number,
                category=category,
                number_of_employees=1,   
                annual_revenue=0.00       
            )
            
        user = User(**validated_data)
        user.set_password(password)
        if company_instance:
            user.company = company_instance
        user.save()

        return user


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class TenderAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenderAttachment
        fields = '__all__'

class BidDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidDocument
        fields = '__all__'
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'
class BidSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )

    status_name = serializers.CharField(
        source='status.name',
        read_only=True
    )

    tender_title = serializers.CharField(
        source='tender.title',
        read_only=True
    )
    
    tender_owner_username = serializers.CharField(
        source='tender.user.username',
        read_only=True
    )

    documents = BidDocumentSerializer(
        many=True, 
        read_only=True
    )

    evaluations = EvaluationSerializer(
        many=True,
        read_only=True,
        source='evaluation_set'
    )

    class Meta:
        model = Bid
        fields = '__all__'
        read_only_fields = [
            'user',
            'creation_date',
            'status'
        ]

    def validate_total_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Total price must be positive"
            )
        return value

    def validate(self, data):
        tender = data.get('tender')
        request = self.context.get('request')

        if tender and request and request.user:
            if tender.user == request.user:
                raise serializers.ValidationError(
                    "You cannot submit a bid on your own tender"
                )

        if tender and tender.deadline < timezone.now():
            raise serializers.ValidationError(
                "Cannot bid on expired tender"
            )
        if tender and tender.status.name == "Closed":
          raise serializers.ValidationError(
            "This tender is closed"
        )
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        from .models import Status
        pending_status, _ = Status.objects.get_or_create(
            name="Pending",
            defaults={"description": "Bid is pending review"}
        )
        validated_data['status'] = pending_status

        return super().create(validated_data)
class TenderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderPayment
        fields = ['amount', 'payment_status', 'payment_date', 'payment_method', 'payment_reference']
class TenderSerializer(serializers.ModelSerializer):

    attachments = TenderAttachmentSerializer(
        many=True,
        read_only=True
    )
    
    bids = BidSerializer(
        many=True,
        read_only=True,
    )
    
    is_saved = serializers.SerializerMethodField()
    
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Tender
        fields = '__all__'
        read_only_fields = [
            'user',
            'is_approved'
        ]

    def to_internal_value(self, data):
        if 'location' in data:
            location_val = data['location']
            
            if isinstance(location_val, str):
                city_name = location_val.strip()
                if not city_name:
                    city_name = "Default City"
                
                location_obj, _ = Location.objects.get_or_create(
                    city=city_name,
                    defaults={
                        'street': 'Pending',
                        'state': city_name
                    }
                )
                data['location'] = location_obj.id
                
            elif isinstance(location_val, int) and (location_val <= 0 or not Location.objects.filter(id=location_val).exists()):
                location_obj, _ = Location.objects.get_or_create(
                    city="Default City",
                    defaults={'street': 'Pending', 'state': 'Default'}
                )
                data['location'] = location_obj.id

        if 'status' in data:
            status_val = data['status']
            if isinstance(status_val, str):
                status_name = status_val.strip()
                status_obj, _ = Status.objects.get_or_create(
                    name=status_name,
                    defaults={'description': f'{status_name} status'}
                )
                data['status'] = status_obj.id
            elif isinstance(status_val, int):
                if not Status.objects.filter(id=status_val).exists():
                    status_obj, _ = Status.objects.get_or_create(
                        name="Open",
                        defaults={'description': 'Default status'}
                    )
                    data['status'] = status_obj.id

        return super().to_internal_value(data)

    def get_payment(self, obj):
        payment = getattr(obj, 'tenderpayment', None)
        if payment:
            return TenderPaymentSerializer(payment).data
        return None

    def validate(self, data):
        if 'budget_min' in data and 'budget_max' in data:
            if data['budget_min'] > data['budget_max']:
                raise serializers.ValidationError(
                    "Min budget cannot exceed max budget"
                )

        if 'deadline' in data and 'start_date' in data:
            if data['deadline'] <= data['start_date']:
                raise serializers.ValidationError(
                    "Deadline must be after start date"
                )

        if 'completion_deadline' in data and 'deadline' in data:
            if data['completion_deadline'] <= data['deadline']:
                raise serializers.ValidationError(
                    "Completion deadline must be after applying deadline"
                )

        if 'deadline' in data:
            if data['deadline'] <= timezone.now():
                raise serializers.ValidationError(
                    "Deadline must be in the future"
                )

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['is_approved'] = False
        return super().create(validated_data)

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedTender.objects.filter(user=request.user, tender=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.category:
            representation['category'] = CategorySerializer(instance.category).data
        if instance.currency:
            representation['currency'] = CurrencySerializer(instance.currency).data
        if instance.location:
            representation['location'] = LocationSerializer(instance.location).data
        if instance.status:
            representation['status'] = StatusSerializer(instance.status).data
            
        return representation

class SavedTenderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SavedTender
        fields = ['id', 'user', 'tender']
        validators = [] 

    def create(self, validated_data):
        saved_tender, created = SavedTender.objects.get_or_create(
            user=validated_data['user'],
            tender=validated_data['tender']
        )
        return saved_tender





class CategoryCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryCompany
        fields = '__all__'


class CategoryTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTender
        fields = '__all__'


class TenderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderStatusHistory
        fields = '__all__'


class BidStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BidStatusHistory
        fields = '__all__'
        



class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
class OTPSerializer(serializers.ModelSerializer):

    class Meta:
        model = OTP
        fields = '__all__'