from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    MetricType, MetricTarget, DailyMetric, 
    BodyMeasurement, TrainingSession
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class MetricTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricType
        fields = '__all__'


class MetricTargetSerializer(serializers.ModelSerializer):
    metric_type = MetricTypeSerializer(read_only=True)
    current_value = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = MetricTarget
        fields = [
            'id', 'metric_type', 'target_type', 'value', 
            'valid_from', 'valid_to', 'is_active', 'current_value'
        ]


class DailyMetricSerializer(serializers.ModelSerializer):
    metric_type = MetricTypeSerializer(read_only=True)
    metric_type_id = serializers.PrimaryKeyRelatedField(
        queryset=MetricType.objects.all(), 
        source='metric_type',
        write_only=True
    )
    
    class Meta:
        model = DailyMetric
        fields = [
            'id', 'date', 'metric_type', 'metric_type_id', 
            'value', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'date': {'required': False}
        }


class MetricsUpdateSerializer(serializers.Serializer):
    """Сериализатор для массового обновления метрик"""
    date = serializers.DateField(required=False)
    metrics = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True),
        required=True
    )
    
    def validate(self, data):
        # Проверяем, что все метрики существуют
        metric_codes = list(data['metrics'].keys())
        existing_metrics = MetricType.objects.filter(
            code__in=metric_codes, 
            is_active=True
        ).values_list('code', flat=True)
        
        invalid_metrics = set(metric_codes) - set(existing_metrics)
        if invalid_metrics:
            raise serializers.ValidationError({
                'metrics': f'Неизвестные метрики: {", ".join(invalid_metrics)}'
            })
        
        return data


class BodyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyMeasurement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'user']


class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'user']


class GradeSerializer(serializers.Serializer):
    """Сериализатор для расчета оценки"""
    date = serializers.DateField()
    grade = serializers.CharField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    category_scores = serializers.DictField(child=serializers.DecimalField(max_digits=5, decimal_places=2))
    force_majeure = serializers.BooleanField()


class DashboardSerializer(serializers.Serializer):
    """Сериализатор для дашборда"""
    date = serializers.DateField()
    metrics = DailyMetricSerializer(many=True)
    body_measurement = BodyMeasurementSerializer(required=False, allow_null=True)
    trainings = TrainingSessionSerializer(many=True)
    progress = serializers.DictField()


class TrendSerializer(serializers.Serializer):
    """Сериализатор для трендов"""
    metric = serializers.CharField()
    unit = serializers.CharField()
    values = serializers.ListField(
        child=serializers.DictField()
    )
    