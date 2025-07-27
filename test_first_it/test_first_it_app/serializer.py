from rest_framework import serializers
from django.utils import timezone
from .models import CashFlow, StatusType, OperationType, Category, Subcategory


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusType
        fields = [
            'name'
        ]


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationType
        fields = [
            'name'
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name'
        ]


class SubcategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Subcategory
        fields = [
            'id',
            'name',
            'category'
        ]


class CashFlowSerializer(serializers.ModelSerializer):
    category = SubcategorySerializer(read_only=True)
    type = OperationSerializer(read_only=True)
    status = StatusSerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategory.objects.all(), 
        source='category',
        write_only=True
    )
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=OperationType.objects.all(),
        source='type',
        write_only=True
    )
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=StatusType.objects.all(),
        source='status',
        write_only=True
    )

    class Meta:
        model = CashFlow
        fields = [
            'id',
            'amount',
            'comment',
            'created_at',
            'category',
            'type',
            'status',
            'category_id',
            'type_id',
            'status_id'
        ]
