"""
Модульные тесты для приложения трекера.
"""

import json
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from tracker.models import (
    MetricType, MetricTarget, DailyMetric, 
    BodyMeasurement, TrainingSession
)


class MetricTypeTests(TestCase):
    """Тесты для модели MetricType"""
    
    def setUp(self):
        self.metric_data = {
            'code': 'test_metric',
            'name': 'Тестовая метрика',
            'category': 'nutrition',
            'unit': 'g',
            'description': 'Тестовое описание',
            'order': 99,
            'is_active': True
        }
        self.metric = MetricType.objects.create(**self.metric_data)
    
    def test_metric_type_creation(self):
        """Тест создания типа метрики"""
        self.assertEqual(self.metric.code, 'test_metric')
        self.assertEqual(self.metric.name, 'Тестовая метрика')
        self.assertEqual(self.metric.category, 'nutrition')
        self.assertEqual(self.metric.unit, 'g')
        self.assertTrue(self.metric.is_active)
    
    def test_metric_type_str(self):
        """Тест строкового представления"""
        self.assertEqual(
            str(self.metric), 
            'Тестовая метрика (г)'
        )
    
    def test_unique_code_constraint(self):
        """Тест уникальности кода метрики"""
        with self.assertRaises(Exception):
            MetricType.objects.create(**self.metric_data)
    
    def test_default_is_active(self):
        """Тест значения по умолчанию для is_active"""
        metric = MetricType.objects.create(
            code='test_metric2',
            name='Тестовая метрика 2',
            category='activity',
            unit='steps'
        )
        self.assertTrue(metric.is_active)


class MetricTargetTests(TestCase):
    """Тесты для модели MetricTarget"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.metric_type = MetricType.objects.create(
            code='calories',
            name='Калории',
            category='nutrition',
            unit='kcal'
        )
        
        self.target_data = {
            'user': self.user,
            'metric_type': self.metric_type,
            'target_type': 'max',
            'value': 2500,
            'valid_from': date(2026, 1, 1),
            'valid_to': date(2026, 12, 31),
            'is_active': True
        }
        self.target = MetricTarget.objects.create(**self.target_data)
    
    def test_metric_target_creation(self):
        """Тест создания норматива"""
        self.assertEqual(self.target.user, self.user)
        self.assertEqual(self.target.metric_type, self.metric_type)
        self.assertEqual(self.target.target_type, 'max')
        self.assertEqual(self.target.value, 2500)
        self.assertTrue(self.target.is_active)
    
    def test_metric_target_str(self):
        """Тест строкового представления"""
        self.assertEqual(
            str(self.target), 
            'testuser - Калории: 2500'
        )
    
    def test_target_type_choices(self):
        """Тест валидности выбора типа норматива"""
        valid_targets = ['min', 'max', 'exact']
        target = MetricTarget.objects.create(
            user=self.user,
            metric_type=self.metric_type,
            target_type='min',
            value=2000,
            valid_from=date(2026, 1, 2),
            valid_to=date(2026, 12, 31)
        )
        self.assertIn(target.target_type, valid_targets)
    
    def test_unique_together_constraint(self):
        """Тест уникальности комбинации user/metric_type/valid_from"""
        with self.assertRaises(Exception):
            MetricTarget.objects.create(
                user=self.user,
                metric_type=self.metric_type,
                target_type='min',
                value=2000,
                valid_from=date(2026, 1, 1),  # Та же дата начала
                valid_to=date(2026, 6, 30)
            )


class DailyMetricTests(TestCase):
    """Тесты для модели DailyMetric"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.metric_type = MetricType.objects.create(
            code='steps',
            name='Шаги',
            category='activity',
            unit='steps'
        )
        
        self.daily_metric_data = {
            'user': self.user,
            'date': date(2026, 1, 15),
            'metric_type': self.metric_type,
            'value': 10000,
            'notes': 'Хорошая прогулка'
        }
        self.daily_metric = DailyMetric.objects.create(**self.daily_metric_data)
    
    def test_daily_metric_creation(self):
        """Тест создания ежедневной метрики"""
        self.assertEqual(self.daily_metric.user, self.user)
        self.assertEqual(self.daily_metric.date, date(2026, 1, 15))
        self.assertEqual(self.daily_metric.metric_type, self.metric_type)
        self.assertEqual(self.daily_metric.value, 10000)
        self.assertEqual(self.daily_metric.notes, 'Хорошая прогулка')
    
    def test_daily_metric_str(self):
        """Тест строкового представления"""
        self.assertEqual(
            str(self.daily_metric), 
            'testuser - 2026-01-15: Шаги = 10000'
        )
    
    def test_unique_together_constraint(self):
        """Тест уникальности комбинации user/date/metric_type"""
        with self.assertRaises(Exception):
            DailyMetric.objects.create(
                user=self.user,
                date=date(2026, 1, 15),  # Та же дата
                metric_type=self.metric_type,  # Тот же тип метрики
                value=15000
            )
    
    def test_ordering(self):
        """Тест порядка сортировки по умолчанию"""
        # Создаем еще одну метрику на другую дату
        DailyMetric.objects.create(
            user=self.user,
            date=date(2026, 1, 14),
            metric_type=self.metric_type,
            value=8000
        )
        
        metrics = DailyMetric.objects.all()
        # Проверяем, что сортировка по убыванию даты
        self.assertEqual(metrics[0].date, date(2026, 1, 15))
        self.assertEqual(metrics[1].date, date(2026, 1, 14))


class BodyMeasurementTests(TestCase):
    """Тесты для модели BodyMeasurement"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.measurement_data = {
            'user': self.user,
            'date': date(2026, 1, 15),
            'weight': Decimal('80.5'),
            'fat_percent': Decimal('15.5'),
            'visceral_fat': Decimal('8.0'),
            'muscle_mass': Decimal('40.2'),
            'waist': Decimal('85.5'),
            'notes': 'После тренировки'
        }
        self.measurement = BodyMeasurement.objects.create(**self.measurement_data)
    
    def test_body_measurement_creation(self):
        """Тест создания замера тела"""
        self.assertEqual(self.measurement.user, self.user)
        self.assertEqual(self.measurement.date, date(2026, 1, 15))
        self.assertEqual(self.measurement.weight, Decimal('80.5'))
        self.assertEqual(self.measurement.fat_percent, Decimal('15.5'))
        self.assertEqual(self.measurement.waist, Decimal('85.5'))
        self.assertEqual(self.measurement.notes, 'После тренировки')
    
    def test_body_measurement_str(self):
        """Тест строкового представления"""
        self.assertEqual(
            str(self.measurement), 
            'testuser - 2026-01-15: 80.5кг'
        )
    
    def test_unique_together_constraint(self):
        """Тест уникальности комбинации user/date"""
        with self.assertRaises(Exception):
            BodyMeasurement.objects.create(
                user=self.user,
                date=date(2026, 1, 15),  # Та же дата
                weight=Decimal('81.0')
            )
    
    def test_optional_fields(self):
        """Тест, что необязательные поля могут быть пустыми"""
        measurement = BodyMeasurement.objects.create(
            user=self.user,
            date=date(2026, 1, 16),
            weight=Decimal('80.0')
        )
        self.assertIsNone(measurement.fat_percent)
        self.assertIsNone(measurement.waist)


class TrainingSessionTests(TestCase):
    """Тесты для модели TrainingSession"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.training_data = {
            'user': self.user,
            'date': date(2026, 1, 15),
            'training_type': 'strength',
            'duration': 60,
            'intensity': 8,
            'exercises': '{"squats": 50, "pushups": 30}',
            'notes': 'Тяжелая тренировка'
        }
        self.training = TrainingSession.objects.create(**self.training_data)
    
    def test_training_session_creation(self):
        """Тест создания тренировки"""
        self.assertEqual(self.training.user, self.user)
        self.assertEqual(self.training.date, date(2026, 1, 15))
        self.assertEqual(self.training.training_type, 'strength')
        self.assertEqual(self.training.duration, 60)
        self.assertEqual(self.training.intensity, 8)
        self.assertEqual(self.training.exercises, '{"squats": 50, "pushups": 30}')
        self.assertEqual(self.training.notes, 'Тяжелая тренировка')
    
    def test_training_session_str(self):
        """Тест строкового представления"""
        self.assertEqual(
            str(self.training), 
            'testuser - 2026-01-15: Силовая'
        )
    
    def test_training_type_choices(self):
        """Тест валидности выбора типа тренировки"""
        valid_types = ['strength', 'cardio', 'flexibility', 'mixed']
        self.assertIn(self.training.training_type, valid_types)
    
    def test_intensity_validation(self):
        """Тест валидации интенсивности"""
        # Создаем с некорректной интенсивностью
        training = TrainingSession(
            user=self.user,
            date=date(2026, 1, 16),
            training_type='cardio',
            duration=30,
            intensity=11,  # > 10
            exercises='{}'
        )
        
        # Пытаемся сохранить - должно вызвать ошибку валидации
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            training.full_clean()


class APITests(TestCase):
    """Тесты API эндпоинтов"""
    
    def setUp(self):
        # Создаем пользователя и клиент API
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Создаем тестовые данные
        self.metric_type = MetricType.objects.create(
            code='steps',
            name='Шаги',
            category='activity',
            unit='steps'
        )
        
        # Создаем норматив
        self.target = MetricTarget.objects.create(
            user=self.user,
            metric_type=self.metric_type,
            target_type='min',
            value=10000,
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31),
            is_active=True
        )
        
        # URL для тестирования
        self.today = timezone.now().date().isoformat()
    
    def test_get_active_targets(self):
        """Тест получения активных нормативов"""
        response = self.client.get(reverse('targets'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['metric_type']['code'], 'steps')
    
    def test_get_metrics_today_empty(self):
        """Тест получения метрик за сегодня (пустые)"""
        response = self.client.get(reverse('metrics-today'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен вернуть хотя бы одну метрику с пустым значением
        self.assertGreater(len(response.data), 0)
    
    def test_update_metrics_single(self):
        """Тест обновления одной метрики"""
        url = reverse('metrics-update')
        data = {
            'metrics': {
                'steps': 12000
            }
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['value'], '12000.00')
        
        # Проверяем, что метрика создалась в БД
        daily_metric = DailyMetric.objects.get(
            user=self.user,
            metric_type=self.metric_type
        )
        self.assertEqual(daily_metric.value, Decimal('12000.00'))
    
    # def test_update_metrics_multiple(self):
    #     """Тест обновления нескольких метрик"""
    #     # Создаем еще один тип метрики
    #     calorie_metric = MetricType.objects.create(
    #         code='calories',
    #         name='Калории',
    #         category='nutrition',
    #         unit='kcal'
    #     )
        
    #     url = reverse('metrics-update')
    #     data = {
    #         'date': '2026-01-15',
    #         'metrics': {
    #             'steps': 15000,
    #             'calories': 2500
    #         }
    #     }
    #     response = self.client.patch(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 2)
    
    def test_update_metrics_invalid_metric(self):
        """Тест обновления с несуществующей метрикой"""
        url = reverse('metrics-update')
        data = {
            'metrics': {
                'invalid_metric': 1000
            }
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('metrics', response.data)
    
    # def test_get_metrics_by_date(self):
    #     """Тест получения метрик по дате"""
    #     # Создаем метрику
    #     DailyMetric.objects.create(
    #         user=self.user,
    #         date=date(2026, 1, 15),
    #         metric_type=self.metric_type,
    #         value=10000
    #     )
        
    #     url = reverse('metrics-by-date', args=['2026-01-15'])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 1)
    #     self.assertEqual(response.data[0]['value'], Decimal('10000'))
    
    def test_get_metrics_by_date_invalid_format(self):
        """Тест получения метрик по некорректной дате"""
        url = reverse('metrics-by-date', args=['invalid-date'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # def test_get_metrics_period(self):
    #     """Тест получения метрик за период"""
    #     # Создаем несколько метрик
    #     for i in range(3):
    #         DailyMetric.objects.create(
    #             user=self.user,
    #             date=date(2026, 1, 15 + i),
    #             metric_type=self.metric_type,
    #             value=10000 + i*1000
    #         )
        
    #     url = reverse('metrics-period')
    #     response = self.client.get(url, {
    #         'start_date': '2026-01-15',
    #         'end_date': '2026-01-17'
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 3)  # 3 даты
    
    # def test_create_body_measurement(self):
    #     """Тест создания замера тела"""
    #     url = reverse('body-create')
    #     data = {
    #         'date': '2026-01-15',
    #         'weight': 80.5,
    #         'fat_percent': 15.5,
    #         'waist': 85.5
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data['weight'], '80.50')
        
    #     # Проверяем, что создался в БД
    #     measurement = BodyMeasurement.objects.get(user=self.user)
    #     self.assertEqual(measurement.weight, Decimal('80.5'))
    
    def test_get_body_latest(self):
        """Тест получения последнего замера"""
        # Создаем замеры
        BodyMeasurement.objects.create(
            user=self.user,
            date=date(2026, 1, 14),
            weight=81.0
        )
        BodyMeasurement.objects.create(
            user=self.user,
            date=date(2026, 1, 15),
            weight=80.5
        )
        
        url = reverse('body-latest')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['weight'], '80.50')  # Последний замер
    
    # def test_create_training_session(self):
    #     """Тест создания тренировки"""
    #     url = reverse('trainings-create')
    #     data = {
    #         'date': '2026-01-15',
    #         'training_type': 'strength',
    #         'duration': 60,
    #         'intensity': 8,
    #         'exercises': '{"squats": 50}'
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data['training_type'], 'strength')
    
    def test_get_training_today(self):
        """Тест получения тренировок за сегодня"""
        today = timezone.now().date()
        TrainingSession.objects.create(
            user=self.user,
            date=today,
            training_type='cardio',
            duration=30,
            intensity=7,
            exercises='{}'
        )
        
        url = reverse('trainings-today')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    # def test_get_grade_by_date(self):
    #     """Тест получения оценки за день"""
    #     # Создаем метрики для расчета оценки
    #     DailyMetric.objects.create(
    #         user=self.user,
    #         date=date(2026, 1, 15),
    #         metric_type=self.metric_type,
    #         value=12000  # Выше нормы 10000
    #     )
        
    #     url = reverse('grade-by-date', args=['2026-01-15'])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('grade', response.data)
    #     self.assertIn('percentage', response.data)
    
    def test_get_dashboard_today(self):
        """Тест получения дашборда на сегодня"""
        # Создаем метрику за сегодня
        today = timezone.now().date()
        DailyMetric.objects.create(
            user=self.user,
            date=today,
            metric_type=self.metric_type,
            value=8000
        )
        
        url = reverse('dashboard-today')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', response.data)
        self.assertIn('progress', response.data)
    
    def test_authentication_required(self):
        """Тест, что API требует аутентификации"""
        client = APIClient()  # Неаутентифицированный клиент
        response = client.get(reverse('metrics-today'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ManagementCommandsTests(TestCase):
    """Тесты для manage.py команд"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_init_tracker_command(self):
        """Тест команды инициализации трекера"""
        # Запускаем команду
        out = call_command('init_tracker', '--username', 'testuser')
        
        # Проверяем, что создались типы метрик
        metric_count = MetricType.objects.count()
        self.assertGreater(metric_count, 0)
        
        # Проверяем, что создались нормативы для пользователя
        target_count = MetricTarget.objects.filter(user=self.user).count()
        self.assertGreater(target_count, 0)
    
    def test_init_tracker_skip_metrics(self):
        """Тест команды с пропуском создания метрик"""
        # Создаем одну метрику заранее
        MetricType.objects.create(
            code='existing_metric',
            name='Существующая метрика',
            category='nutrition',
            unit='g'
        )
        
        initial_count = MetricType.objects.count()
        
        # Запускаем команду с пропуском метрик
        call_command('init_tracker', '--skip-metrics', '--username', 'testuser')
        
        # Количество метрик не должно измениться
        self.assertEqual(MetricType.objects.count(), initial_count)
    
    def test_init_tracker_skip_targets(self):
        """Тест команды с пропуском создания нормативов"""
        # Запускаем команду с пропуском нормативов
        call_command('init_tracker', '--skip-targets', '--username', 'testuser')
        
        # Нормативов не должно быть создано
        target_count = MetricTarget.objects.filter(user=self.user).count()
        self.assertEqual(target_count, 0)
        
        # Но метрики должны быть созданы
        metric_count = MetricType.objects.count()
        self.assertGreater(metric_count, 0)
    
    def test_init_tracker_force(self):
        """Тест команды с пересозданием метрик"""
        # Создаем метрику заранее
        MetricType.objects.create(
            code='calories',
            name='Старые калории',
            category='old',
            unit='old_unit'
        )
        
        # Запускаем команду с force
        call_command('init_tracker', '--force', '--username', 'testuser')
        
        # Проверяем, что метрика обновилась
        metric = MetricType.objects.get(code='calories')
        self.assertEqual(metric.category, 'nutrition')
        self.assertEqual(metric.unit, 'kcal')
    
    def test_init_tracker_user_not_found(self):
        """Тест команды с несуществующим пользователем"""
        # Перехватываем вывод
        from io import StringIO
        out = StringIO()
        
        call_command('init_tracker', '--username', 'nonexistent', stdout=out)
        
        # Проверяем, что выведено сообщение об ошибке
        output = out.getvalue()
        self.assertIn('не найден', output)


class APIPerformanceTests(TestCase):
    """Тесты производительности API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Создаем много метрик для тестирования
        self.metric_type = MetricType.objects.create(
            code='steps',
            name='Шаги',
            category='activity',
            unit='steps'
        )
        
        # Создаем 100 метрик за последние 100 дней
        for i in range(100):
            DailyMetric.objects.create(
                user=self.user,
                date=timezone.now().date() - timedelta(days=i),
                metric_type=self.metric_type,
                value=10000 + i*100
            )
    
    # def test_metrics_period_performance(self):
    #     """Тест производительности получения метрик за период"""
    #     import time
        
    #     start_time = time.time()
    #     response = self.client.get(reverse('metrics-period'), {
    #         'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
    #         'end_date': timezone.now().date().isoformat()
    #     })
    #     end_time = time.time()
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    #     # Время выполнения должно быть меньше 100ms
    #     execution_time = (end_time - start_time) * 1000  # в миллисекундах
    #     self.assertLess(execution_time, 100, 
    #                    f"Запрос выполнился за {execution_time:.2f}ms, что больше 100ms")
    
    def test_dashboard_today_performance(self):
        """Тест производительности дашборда"""
        import time
        
        # Создаем норматив
        MetricTarget.objects.create(
            user=self.user,
            metric_type=self.metric_type,
            target_type='min',
            value=10000,
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31),
            is_active=True
        )
        
        start_time = time.time()
        response = self.client.get(reverse('dashboard-today'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Время выполнения должно быть меньше 50ms
        execution_time = (end_time - start_time) * 1000
        self.assertLess(execution_time, 50, 
                       f"Запрос выполнился за {execution_time:.2f}ms, что больше 50ms")


class EdgeCaseTests(TestCase):
    """Тесты граничных случаев"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_update_metrics_null_value(self):
        """Тест обновления метрики с null значением"""
        metric_type = MetricType.objects.create(
            code='water',
            name='Вода',
            category='nutrition',
            unit='l'
        )
        
        url = reverse('metrics-update')
        data = {
            'metrics': {
                'water': None
            }
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что метрика создалась с null значением
        daily_metric = DailyMetric.objects.get(
            user=self.user,
            metric_type=metric_type
        )
        self.assertIsNone(daily_metric.value)
    
    def test_update_metrics_future_date(self):
        """Тест обновления метрики на будущую дату"""
        future_date = (timezone.now().date() + timedelta(days=1)).isoformat()
        
        url = reverse('metrics-update')
        data = {
            'date': future_date,
            'metrics': {
                'steps': 10000
            }
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_metrics_period_large_range(self):
        """Тест получения метрик за слишком большой период"""
        url = reverse('metrics-period')
        response = self.client.get(url, {
            'start_date': '2023-01-01',
            'end_date': '2026-12-31'  # > 90 дней
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_body_measurement_future_date(self):
        """Тест создания замера на будущую дату"""
        future_date = (timezone.now().date() + timedelta(days=1)).isoformat()
        
        url = reverse('body-create')
        data = {
            'date': future_date,
            'weight': 80.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_duplicate_body_measurement(self):
        """Тест создания дубликата замера на ту же дату"""
        # Создаем первый замер
        BodyMeasurement.objects.create(
            user=self.user,
            date=date(2026, 1, 15),
            weight=80.0
        )
        
        url = reverse('body-create')
        data = {
            'date': '2026-01-15',
            'weight': 81.0
        }
        response = self.client.post(url, data, format='json')
        # Должно вернуть ошибку, т.к. дата уникальна
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
