from rest_framework import viewsets, status, permissions
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


@extend_schema(tags=["Tracker"])
class ActiveTargetsView(APIView):
    """Активные нормативы на сегодня"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Получаем активные нормативы
        targets = MetricTarget.objects.filter(
            user=request.user,
            is_active=True,
            valid_from__lte=today,
            valid_to__gte=today
        ).select_related('metric_type')
        
        # Получаем текущие значения за сегодня
        daily_metrics = DailyMetric.objects.filter(
            user=request.user,
            date=today,
            metric_type__in=[t.metric_type for t in targets]
        ).select_related('metric_type')
        
        # Создаем словарь значений для быстрого доступа
        value_dict = {dm.metric_type.id: dm.value for dm in daily_metrics}
        
        # Сериализуем нормативы с текущими значениями
        result = []
        for target in targets:
            target_data = MetricTargetSerializer(target).data
            target_data['current_value'] = value_dict.get(target.metric_type.id)
            result.append(target_data)
        
        return Response(result)


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


@extend_schema(tags=["Tracker"])
class DailyMetricByDateView(APIView):
    """Метрики за конкретную дату"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, date_str):
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if target_date > timezone.now().date():
            return Response(
                {'error': 'Дата не может быть в будущем.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        metrics = DailyMetric.objects.filter(
            user=request.user,
            date=target_date
        ).select_related('metric_type')
        
        serializer = DailyMetricSerializer(metrics, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class DailyMetricPeriodView(APIView):
    """Метрики за период"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if not start_date_str or not end_date_str:
            return Response(
                {'error': 'Необходимо указать start_date и end_date.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if start_date > end_date:
            return Response(
                {'error': 'start_date должен быть меньше или равен end_date.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ограничение периода 90 днями
        if (end_date - start_date).days > 90:
            return Response(
                {'error': 'Период не может превышать 90 дней.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем метрики за период
        metrics = DailyMetric.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).select_related('metric_type').order_by('date')
        
        # Группируем по датам
        grouped_data = {}
        for metric in metrics:
            date_key = metric.date.isoformat()
            if date_key not in grouped_data:
                grouped_data[date_key] = []
            
            grouped_data[date_key].append(DailyMetricSerializer(metric).data)
        
        return Response(grouped_data)


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
class BodyMeasurementListView(APIView):
    """История замеров тела"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        measurements = BodyMeasurement.objects.filter(
            user=request.user
        ).order_by('-date')[offset:offset + limit]
        
        serializer = BodyMeasurementSerializer(measurements, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class BodyMeasurementLatestView(APIView):
    """Последний замер тела"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        measurement = BodyMeasurement.objects.filter(
            user=request.user
        ).order_by('-date').first()
        
        if not measurement:
            return Response({})
        
        serializer = BodyMeasurementSerializer(measurement)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class BodyMeasurementByDateView(APIView):
    """Замер тела на конкретную дату"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, date_str):
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        measurement = BodyMeasurement.objects.filter(
            user=request.user,
            date=target_date
        ).first()
        
        if not measurement:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BodyMeasurementSerializer(measurement)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class BodyMeasurementCreateView(APIView):
    """Создание нового замера тела"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BodyMeasurementSerializer(data=request.data)
        if serializer.is_valid():
            # Проверяем дату
            measurement_date = serializer.validated_data.get('date', timezone.now().date())
            if measurement_date > timezone.now().date():
                return Response(
                    {'error': 'Дата не может быть в будущем.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Сохраняем с текущим пользователем
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Tracker"])
class TrainingSessionTodayView(APIView):
    """Тренировки за сегодня"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        trainings = TrainingSession.objects.filter(
            user=request.user,
            date=today
        )
        
        serializer = TrainingSessionSerializer(trainings, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class TrainingSessionByDateView(APIView):
    """Тренировки за конкретную дату"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, date_str):
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trainings = TrainingSession.objects.filter(
            user=request.user,
            date=target_date
        )
        
        serializer = TrainingSessionSerializer(trainings, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class TrainingSessionCreateView(APIView):
    """Создание тренировки"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TrainingSessionSerializer(data=request.data)
        if serializer.is_valid():
            # Проверяем дату
            training_date = serializer.validated_data.get('date', timezone.now().date())
            if training_date > timezone.now().date():
                return Response(
                    {'error': 'Дата не может быть в будущем.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Сохраняем с текущим пользователем
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Tracker"])
class GradeByDateView(APIView):
    """Расчет оценки за день"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, date_str):
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if target_date > timezone.now().date():
            return Response(
                {'error': 'Дата не может быть в будущем.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Здесь будет ваша логика расчета оценки
        # Пока возвращаем заглушку
        grade_data = {
            'date': target_date,
            'grade': 'B+',
            'percentage': 78.5,
            'category_scores': {
                'nutrition': 85,
                'activity': 90,
                'intellect': 65,
                'strength': 75
            },
            'force_majeure': False
        }
        
        serializer = GradeSerializer(grade_data)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class GradePeriodView(APIView):
    """Оценки за период"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if not start_date_str or not end_date_str:
            return Response(
                {'error': 'Необходимо указать start_date и end_date.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if start_date > end_date:
            return Response(
                {'error': 'start_date должен быть меньше или равен end_date.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ограничение периода 30 днями
        if (end_date - start_date).days > 30:
            return Response(
                {'error': 'Период не может превышать 30 дней.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Здесь будет логика расчета оценок за период
        # Пока возвращаем заглушку
        grades = []
        current_date = start_date
        while current_date <= end_date:
            if current_date <= timezone.now().date():
                grades.append({
                    'date': current_date,
                    'grade': 'A' if current_date.weekday() < 5 else 'B',
                    'percentage': 85.0 if current_date.weekday() < 5 else 70.0
                })
            current_date += timedelta(days=1)
        
        return Response(grades)


@extend_schema(tags=["Tracker"])
class DashboardTodayView(APIView):
    """Полная сводка за сегодня"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Метрики за сегодня
        metrics = DailyMetric.objects.filter(
            user=request.user,
            date=today
        ).select_related('metric_type')
        
        # Замер тела за сегодня
        body_measurement = BodyMeasurement.objects.filter(
            user=request.user,
            date=today
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
        
        # Рассчитываем прогресс
        progress = {}
        for target in targets:
            current_value = None
            for metric in metrics:
                if metric.metric_type.id == target.metric_type.id:
                    current_value = metric.value
                    break
            
            if current_value is not None:
                if target.target_type == 'min':
                    progress[target.metric_type.code] = {
                        'current': float(current_value),
                        'target': float(target.value),
                        'percentage': min(100, float(current_value) / float(target.value) * 100)
                    }
                elif target.target_type == 'max':
                    progress[target.metric_type.code] = {
                        'current': float(current_value),
                        'target': float(target.value),
                        'percentage': max(0, 100 - (float(current_value) / float(target.value) * 100))
                    }
                else:  # exact
                    progress[target.metric_type.code] = {
                        'current': float(current_value),
                        'target': float(target.value),
                        'percentage': 100 if float(current_value) == float(target.value) else 0
                    }
        
        data = {
            'date': today,
            'metrics': DailyMetricSerializer(metrics, many=True).data,
            'body_measurement': BodyMeasurementSerializer(body_measurement).data if body_measurement else None,
            'trainings': TrainingSessionSerializer(trainings, many=True).data,
            'progress': progress
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
            MetricType, 
            code=metric_code, 
            is_active=True
        )
        
        # Рассчитываем даты
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Получаем данные
        metrics = DailyMetric.objects.filter(
            user=request.user,
            metric_type=metric_type,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Формируем данные для графика
        values = []
        for metric in metrics:
            values.append({
                'date': metric.date,
                'value': float(metric.value)
            })
        
        data = {
            'metric': metric_code,
            'unit': metric_type.unit,
            'values': values
        }
        
        serializer = TrendSerializer(data)
        return Response(serializer.data)


@extend_schema(tags=["Tracker"])
class AnalyticsStreaksView(APIView):
    """Текущие серии выполнения"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Здесь будет логика расчета серий
        # Пока возвращаем заглушку
        return Response({
            'streaks': [
                {'metric': 'steps', 'days': 5, 'current': True},
                {'metric': 'calories', 'days': 3, 'current': True},
                {'metric': 'sleep', 'days': 7, 'current': False}
            ]
        })
    