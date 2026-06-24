from rest_framework import serializers
from .models import Location, Category, Company, Tender, Bid, BidDocument, CategoryCompany, CategoryTender, TenderStatusHistory, BidStatusHistory, Status, User, Currency, TenderAttachment, Notification, OTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q
from .models import *
from django.utils import timezone

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


class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_company_name(self, obj):
        if obj.company:
            return obj.company.company_name
        return "No Company"

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
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
        return super().create(validated_data)

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

    class Meta:
        model = Tender
        fields = '__all__'
        read_only_fields = [
            'user',
            'is_approved'
        ]

    def validate(self, data):
        if data['budget_min'] > data['budget_max']:
            raise serializers.ValidationError(
                "Min budget cannot exceed max budget"
            )

        if data['deadline'] <= data['start_date']:
            raise serializers.ValidationError(
                "Deadline must be after start date"
            )

        if data['completion_deadline'] <= data['deadline']:
            raise serializers.ValidationError(
                "Completion deadline must be after applying deadline"
            )

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

    def create(self, validated_data):

        validated_data['user'] = self.context['request'].user

        validated_data['is_approved'] = False

        return super().create(validated_data)
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedTender.objects.filter(user=request.user, tender=obj).exists()
        return False

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


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'


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
        

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
class OTPSerializer(serializers.ModelSerializer):

    class Meta:
        model = OTP
        fields = '__all__'