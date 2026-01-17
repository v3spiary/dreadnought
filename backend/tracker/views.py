from rest_framework import viewsets, status, permissions
from django.db.models import F, Window, Case, When, Value, CharField
from django.db.models import Subquery, OuterRef, Case, When, Value, FloatField
from django.db.models.functions import Lag
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes
from drf_spectacular.types import OpenApiTypes

from .models import MetricType, MetricTarget, DailyMetric, BodyMeasurement, TrainingSession
from .serializers import (
    MetricTargetSerializer, DailyMetricSerializer, MetricsUpdateSerializer,
    BodyMeasurementSerializer, TrainingSessionSerializer, GradeSerializer,
    DashboardSerializer, TrendSerializer
)


@extend_schema(
    tags=["Tracker"],
    summary="Обновление метрик",
    description="Универсальный метод для создания/обновления метрик. Если метрика существует - обновляет значение, если нет - создаёт.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'date': {
                    'type': 'string',
                    'format': 'date',
                    'description': 'Дата (опционально, по умолчанию сегодня)',
                    'example': '2024-01-15'
                },
                'metrics': {
                    'type': 'object',
                    'description': 'Словарь метрик {код_метрики: значение}',
                    'example': {
                        'calories': 2500,
                        'protein': 180,
                        'steps': 12500,
                        'sleep': 7.5
                    }
                }
            }
        }
    },
    responses={
        200: DailyMetricSerializer(many=True),
        400: {
            'type': 'object',
            'properties': {
                'errors': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['Метрика "unknown_metric" не найдена или не активна.']
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            'Пример обновления метрик',
            value={
                'date': '2024-01-15',
                'metrics': {
                    'calories': 2500,
                    'protein': 180,
                    'steps': 12500,
                    'sleep': 7.5,
                    'water': 2.5
                }
            },
            request_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Без указания даты (сегодня)',
            value={
                'metrics': {
                    'calories': 2200,
                    'steps': 8000
                }
            },
            request_only=True,
            status_codes=['200']
        )
    ]
)
class DailyMetricUpdateView(APIView):
    """Универсальное создание/обновление метрик (PATCH)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request):
        serializer = MetricsUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        target_date = data.get('date', timezone.now().date())
        metrics_dict = data.get('metrics', {})
        
        if target_date > timezone.now().date():
            return Response(
                {'error': 'Дата не может быть в будущем.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем объекты типов метрик по кодам
        metric_types = MetricType.objects.filter(
            code__in=metrics_dict.keys(),
            is_active=True
        )
        
        metric_type_dict = {mt.code: mt for mt in metric_types}
        
        updated_metrics = []
        errors = []
        
        for code, value in metrics_dict.items():
            if code not in metric_type_dict:
                errors.append(f'Метрика "{code}" не найдена или не активна.')
                continue
            
            metric_type = metric_type_dict[code]
            
            # Создаем или обновляем метрику
            daily_metric, created = DailyMetric.objects.update_or_create(
                user=request.user,
                date=target_date,
                metric_type=metric_type,
                defaults={'value': value}
            )
            
            updated_metrics.append(DailyMetricSerializer(daily_metric).data)
        
        if errors:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(updated_metrics)


@extend_schema(tags=["Tracker"])
class DashboardTodayView(APIView):
    """Полная сводка за сегодня с трендами"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Метрики за сегодня с трендами
        metrics_today = DailyMetric.objects.filter(
            user=request.user,
            date=today
        ).select_related('metric_type')
        
        # Получаем значения за вчера для тех же типов метрик
        metric_type_ids = metrics_today.values_list('metric_type_id', flat=True)
        
        # Создаем подзапрос для получения вчерашних значений
        yesterday_values = DailyMetric.objects.filter(
            user=request.user,
            metric_type=OuterRef('metric_type'),
            date=yesterday
        ).values('value')[:1]
        
        # Аннотируем сегодняшние метрики вчерашними значениями
        metrics_with_trend = metrics_today.annotate(
            yesterday_value=Subquery(yesterday_values, output_field=FloatField())
        )
        
        # Замер тела за сегодня
        body_measurement = BodyMeasurement.objects.filter(
            user=request.user,
            date=today
        ).first()
        
        # Получаем замер тела за вчера для расчета тренда
        body_measurement_yesterday = None
        if body_measurement:
            body_measurement_yesterday = BodyMeasurement.objects.filter(
                user=request.user,
                date=yesterday
            ).first()
        
        # Тренировки за сегодня
        trainings = TrainingSession.objects.filter(
            user=request.user,
            date=today
        )
        
        # Активные нормативы
        targets = MetricTarget.objects.filter(
            user=request.user,
            is_active=True,
            valid_from__lte=today,
            valid_to__gte=today
        ).select_related('metric_type')
        
        # Рассчитываем прогресс и тренды
        progress = {}
        for target in targets:
            current_value = None
            yesterday_value = None
            
            # Ищем текущее значение метрики
            for metric in metrics_with_trend:
                if metric.metric_type.id == target.metric_type.id:
                    current_value = metric.value
                    yesterday_value = metric.yesterday_value
                    break
            
            progress_data = {
                'current': float(current_value) if current_value is not None else None,
                'target': float(target.value),
                'percentage': 0
            }
            
            # Добавляем тренд
            if current_value is not None and yesterday_value is not None:
                if current_value > yesterday_value:
                    progress_data['trend'] = 'up'
                elif current_value < yesterday_value:
                    progress_data['trend'] = 'down'
                else:
                    progress_data['trend'] = 'stable'
                
                # Рассчитываем изменение
                progress_data['change'] = float(float(current_value) - yesterday_value)
                
                # Рассчитываем процентное изменение
                if yesterday_value != 0:
                    progress_data['change_percent'] = float(
                        (float(current_value) - yesterday_value) / abs(yesterday_value) * 100
                    )
                else:
                    progress_data['change_percent'] = 0
            else:
                progress_data['trend'] = 'no_data'
                progress_data['change'] = None
                progress_data['change_percent'] = None
            
            # Рассчитываем процент выполнения цели
            if current_value is not None:
                if target.target_type == 'min':
                    progress_data['percentage'] = min(100, float(current_value) / float(target.value) * 100)
                elif target.target_type == 'max':
                    progress_data['percentage'] = max(0, 100 - (float(current_value) / float(target.value) * 100))
                else:  # exact
                    progress_data['percentage'] = 100 if float(current_value) == float(target.value) else 0
            
            progress[target.metric_type.code] = progress_data
        
        # Подготавливаем данные метрик с трендами
        metrics_data = []
        for metric in metrics_with_trend:
            metric_data = DailyMetricSerializer(metric).data
            
            # Добавляем тренд для метрики
            if metric.yesterday_value is not None:
                if metric.value > metric.yesterday_value:
                    metric_data['trend'] = 'up'
                elif metric.value < metric.yesterday_value:
                    metric_data['trend'] = 'down'
                else:
                    metric_data['trend'] = 'stable'
                
                # Рассчитываем изменение
                metric_data['change'] = float(float(metric.value) - metric.yesterday_value)
                
                # Рассчитываем процентное изменение
                if metric.yesterday_value != 0:
                    metric_data['change_percent'] = float(
                        (float(metric.value) - metric.yesterday_value) / abs(metric.yesterday_value) * 100
                    )
                else:
                    metric_data['change_percent'] = 0
            else:
                metric_data['trend'] = 'no_data'
                metric_data['change'] = None
                metric_data['change_percent'] = None
            
            metrics_data.append(metric_data)
        
        # Добавляем тренд для замеров тела
        body_data = None
        if body_measurement:
            body_data = BodyMeasurementSerializer(body_measurement).data
            
            if body_measurement_yesterday:
                # Рассчитываем тренды по ключевым замерам
                measurements_trend = {}
                
                # Пример для веса
                if hasattr(body_measurement, 'weight') and hasattr(body_measurement_yesterday, 'weight'):
                    if body_measurement.weight > body_measurement_yesterday.weight:
                        measurements_trend['weight'] = 'up'
                    elif body_measurement.weight < body_measurement_yesterday.weight:
                        measurements_trend['weight'] = 'down'
                    else:
                        measurements_trend['weight'] = 'stable'
                
                # Добавляем другие замеры по аналогии
                # if hasattr(body_measurement, 'chest') and hasattr(body_measurement_yesterday, 'chest'):
                #     ...
                
                body_data['trends'] = measurements_trend
        
        # Собираем общую статистику по тренировкам
        trainings_data = TrainingSessionSerializer(trainings, many=True).data
        
        # Рассчитываем прогресс по тренировкам (сравнение с вчера)
        training_stats = {
            'today': {
                'count': trainings.count(),
                'total_duration': sum(t.duration_minutes for t in trainings) if trainings.exists() else 0,
                'total_calories': sum(t.calories_burned for t in trainings) if trainings.exists() else 0
            },
            'trend': 'no_data'
        }
        
        data = {
            'date': today,
            'metrics': metrics_data,
            'body_measurement': body_data,
            'trainings': trainings_data,
            'training_stats': training_stats,
            'progress': progress,
            'summary': {
                'metrics_today': len(metrics_data),
                'trainings_today': len(trainings_data),
                'goals_today': len(progress)
            }
        }
        
        serializer = DashboardSerializer(data)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class AnalyticsTrendView(APIView):
    """Тренд метрики"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, metric_code):
        days = int(request.query_params.get('days', 30))
        
        # Проверяем существование метрики
        metric_type = get_object_or_404(
            MetricType.objects.only('code', 'unit', 'is_active'),
            code=metric_code, 
            is_active=True
        )
        
        # Рассчитываем даты
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        metrics = DailyMetric.objects.filter(
            user=request.user,
            metric_type=metric_type,
            date__range=[start_date, end_date]
        ).annotate(
            # Получаем значение за предыдущий день
            prev_value=Window(
                expression=Lag('value'),
                partition_by=['user', 'metric_type'],
                order_by=F('date').asc()
            )
        ).annotate(
            # Вычисляем тренд
            trend=Case(
                When(
                    prev_value__isnull=True,
                    then=Value('no_data')
                ),
                When(
                    value__gt=F('prev_value'),
                    then=Value('up')
                ),
                When(
                    value__lt=F('prev_value'),
                    then=Value('down')
                ),
                default=Value('stable'),
                output_field=CharField()
            )
        ).order_by('date').only('date', 'value')
        
        # Формируем данные для графика с трендами
        values = []
        for metric in metrics:
            item = {
                'date': metric.date,
                'value': float(metric.value)
            }
            
            # Добавляем тренд только если он вычислен
            if hasattr(metric, 'trend'):
                item['trend'] = metric.trend
                if metric.prev_value is not None:
                    item['change'] = float(metric.value - metric.prev_value)
                    item['change_percent'] = float(
                        ((metric.value - metric.prev_value) / metric.prev_value * 100)
                        if metric.prev_value != 0 else 0
                    )
            
            values.append(item)
        
        # Вычисляем общий тренд за период (между первым и последним значением)
        overall_trend = None
        if len(values) >= 2:
            first_value = values[0]['value']
            last_value = values[-1]['value']
            
            if last_value > first_value:
                overall_trend = 'up'
            elif last_value < first_value:
                overall_trend = 'down'
            else:
                overall_trend = 'stable'
        
        data = {
            'metric': metric_code,
            'unit': metric_type.unit,
            'values': values,
            'overall_trend': overall_trend,
            'period': {
                'start': start_date,
                'end': end_date,
                'days': days
            }
        }
        
        serializer = TrendSerializer(data)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class DailyMetricTodayView(APIView):
    """Все метрики за сегодня"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        return self._get_metrics_for_date(request.user, today)
    
    def _get_metrics_for_date(self, user, target_date):
        # Получаем все активные типы метрик
        metric_types = MetricType.objects.filter(is_active=True)
        
        # Получаем существующие метрики за дату
        existing_metrics = DailyMetric.objects.filter(
            user=user,
            date=target_date
        ).select_related('metric_type')
        
        # Создаем словарь для быстрого доступа
        existing_dict = {em.metric_type.id: em for em in existing_metrics}
        
        # Формируем результат
        result = []
        for metric_type in metric_types:
            if metric_type.id in existing_dict:
                serializer = DailyMetricSerializer(existing_dict[metric_type.id])
                result.append(serializer.data)
            else:
                # Пустой объект для незаполненных метрик
                result.append({
                    'date': target_date,
                    'metric_type': {
                        'id': metric_type.id,
                        'name': metric_type.name,
                        'code': metric_type.code,
                        'category': metric_type.category,
                        'unit': metric_type.unit
                    },
                    'value': None,
                    'notes': '',
                    'created_at': None,
                    'updated_at': None
                })
        
        return Response(result)

