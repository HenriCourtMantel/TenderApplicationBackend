from datetime import timezone

from rest_framework import serializers
from .models import Location, Category, Company, Tender, Bid, BidDocument, CategoryCompany, CategoryTender, TenderStatusHistory, BidStatusHistory, Status, User, Currency, TenderAttachment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q

from .models import *


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD  

    def validate(self, attrs):
        # This part handles the email/phone and password check
        identifier = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(
                Q(email=identifier) |
                Q(phone=identifier)
            )
        except User.DoesNotExist:
            raise AuthenticationFailed("No account found.")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password.")

        if not user.is_active:
            raise AuthenticationFailed("This account is inactive.")

   

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_verified": user.is_verified,
            "user_id": user.id              
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

    class Meta:
        model = User
        fields = '__all__'

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(**validated_data)

        user.set_password(
            validated_data['password']
        )

        user.save()

        return user


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class TenderSerializer(serializers.ModelSerializer):

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

        if data['deadline'] <= timezone.now():
            raise serializers.ValidationError(
                "Deadline must be in the future"
            )

        return data

    def create(self, validated_data):

        validated_data['user'] = self.context['request'].user

        validated_data['is_approved'] = True

        return super().create(validated_data)


class TenderAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderAttachment
        fields = '__all__'


class BidSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bid
        fields = '__all__'

    def validate_total_price(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Total price must be positive"
            )

        return value

    def validate(self, data):

        tender = data.get('tender')

        if tender and tender.deadline < timezone.now():
            raise serializers.ValidationError(
                "Cannot bid on expired tender"
            )

        return data


class BidDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidDocument
        fields = '__all__'


class SavedTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedTender
        fields = '__all__'


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
        
class SavedTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedTender
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'