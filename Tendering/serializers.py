from rest_framework import serializers
from django.db import IntegrityError

from .models import Field, User, Tender, Bid, SavedTender


# -------------------------
# FIELD
# -------------------------
class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'


# -------------------------
# USER
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    # write-only M2M input
    field_ids = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(),
        many=True,
        write_only=True,
        source='fields',
        required=False
    )

    # read-only full representation
    fields_detail = FieldSerializer(
        source='fields',
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'phone',
            'gender',
            'birth_date',
            'company_name',
            'cr_number',
            'field_ids',
            'fields_detail',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if fields_data:
            user.fields.set(fields_data)

        return user

    def update(self, instance, validated_data):
        fields_data = validated_data.pop('fields', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if fields_data is not None:
            instance.fields.set(fields_data)

        return instance


# -------------------------
# TENDER
# -------------------------
class TenderSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    user = UserSerializer(read_only=True)

    field_ids = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(),
        many=True,
        source='fields',
        write_only=True,
        required=False
    )

    fields_detail = FieldSerializer(
        source='fields',
        many=True,
        read_only=True
    )

    class Meta:
        model = Tender
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, data):
        budget_min = data.get('budget_min')
        budget_max = data.get('budget_max')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if budget_min is not None and budget_max is not None:
            if budget_min > budget_max:
                raise serializers.ValidationError({
                    'budget_min': 'Minimum budget cannot exceed maximum budget'
                })

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })

        return data


# -------------------------
# BID
# -------------------------
class BidSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    tender_id = serializers.PrimaryKeyRelatedField(
        queryset=Tender.objects.all(),
        source='tender',
        write_only=True
    )

    user = UserSerializer(read_only=True)
    tender = TenderSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = '__all__'
        read_only_fields = ['id', 'creation_date']

    def validate_total_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total price must be greater than zero")
        return value


# -------------------------
# SAVED TENDER
# -------------------------
class SavedTenderSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    tender_id = serializers.PrimaryKeyRelatedField(
        queryset=Tender.objects.all(),
        source='tender',
        write_only=True
    )

    user = UserSerializer(read_only=True)
    tender = TenderSerializer(read_only=True)

    class Meta:
        model = SavedTender
        fields = '__all__'
        read_only_fields = ['id', 'saved_at']

    def validate(self, data):
        user = data.get('user')
        tender = data.get('tender')

        if user and tender:
            if SavedTender.objects.filter(user=user, tender=tender).exists():
                raise serializers.ValidationError(
                    "This tender is already saved by this user"
                )

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError("This tender is already saved by this user")