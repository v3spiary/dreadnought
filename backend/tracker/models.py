"""Оптимизированные модели БД для трекера."""

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class MetricType(models.Model):
    """Типы метрик, которые можно отслеживать."""

    CATEGORY_CHOICES = [
        ("nutrition", "Питание"),
        ("activity", "Активность"),
        ("intellect", "Интеллект"),
        ("body", "Тело"),
        ("strength", "Силовые"),
    ]

    UNIT_CHOICES = [
        ("kcal", "ккал"),
        ("g", "г"),
        ("l", "л"),
        ("hours", "ч"),
        ("steps", "шагов"),
        ("kg", "кг"),
        ("%", "%"),
        ("count", "шт"),
        ("pages", "стр"),
        ("minutes", "мин"),
    ]

    name = models.CharField(max_length=100, verbose_name="Название метрики")
    code = models.SlugField(max_length=50, unique=True, verbose_name="Код метрики")
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория"
    )
    unit = models.CharField(
        max_length=20, choices=UNIT_CHOICES, verbose_name="Единица измерения"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ["category", "order", "name"]
        verbose_name = "Тип метрики"
        verbose_name_plural = "Типы метрик"

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"


class MetricTarget(models.Model):
    """Нормативы для метрик по пользователям."""

    TARGET_TYPE_CHOICES = [
        ("min", "Минимум"),
        ("max", "Максимум"),
        ("exact", "Точное значение"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="metric_targets"
    )
    metric_type = models.ForeignKey(
        MetricType, on_delete=models.CASCADE, related_name="targets"
    )
    target_type = models.CharField(
        max_length=10, choices=TARGET_TYPE_CHOICES, verbose_name="Тип норматива"
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Значение норматива"
    )
    valid_from = models.DateField(verbose_name="Действует с")
    valid_to = models.DateField(null=True, blank=True, verbose_name="Действует до")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        unique_together = ["user", "metric_type", "valid_from"]
        ordering = ["-valid_from"]
        verbose_name = "Норматив метрики"
        verbose_name_plural = "Нормативы метрик"
        indexes = [
            models.Index(fields=["user", "metric_type", "-valid_from"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.metric_type.name}: {self.value}"


class DailyMetric(models.Model):
    """Ежедневные значения метрик."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_metrics"
    )
    date = models.DateField(db_index=True, verbose_name="Дата")
    metric_type = models.ForeignKey(
        MetricType, on_delete=models.PROTECT, related_name="daily_values"
    )
    value = models.DecimalField(
        max_digits=10, null=True, blank=True, decimal_places=2, verbose_name="Значение"
    )
    notes = models.TextField(blank=True, verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "date", "metric_type"]
        ordering = ["-date", "metric_type__order"]
        verbose_name = "Ежедневная метрика"
        verbose_name_plural = "Ежедневные метрики"
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["date"]),
            models.Index(fields=["user", "-date", "metric_type"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.metric_type.name} = {self.value}"


class BodyMeasurement(models.Model):
    """Замеры тела (вес, процент жира и т.д.)."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="body_measurements"
    )
    date = models.DateField(db_index=True, verbose_name="Дата")

    # Основные замеры
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Вес (кг)"
    )
    fat_percent = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="% жира"
    )
    visceral_fat = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Висцеральный жир",
    )
    muscle_mass = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Мышечная масса (кг)",
    )

    # Дополнительные замеры (можно расширять)
    chest = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Грудь (см)"
    )
    waist = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Талия (см)"
    )
    hips = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Бедра (см)"
    )
    biceps = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Бицепс (см)",
    )

    notes = models.TextField(blank=True, verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]
        verbose_name = "Замер тела"
        verbose_name_plural = "Замеры тела"
        indexes = [
            models.Index(fields=["user", "-date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.weight}кг"


class TrainingSession(models.Model):
    """Тренировочная сессия."""

    TRAINING_TYPE_CHOICES = [
        ("strength", "Силовая"),
        ("cardio", "Кардио"),
        ("flexibility", "Растяжка"),
        ("mixed", "Смешанная"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="training_sessions"
    )
    date = models.DateField(db_index=True, verbose_name="Дата")
    training_type = models.CharField(
        max_length=20, choices=TRAINING_TYPE_CHOICES, verbose_name="Тип тренировки"
    )
    duration = models.PositiveIntegerField(verbose_name="Длительность (мин)")
    intensity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Интенсивность (1-10)",
    )
    exercises = models.TextField(
        verbose_name="Упражнения (JSON или текст)", blank=True, null=True
    )
    notes = models.TextField(blank=True, verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Тренировка"
        verbose_name_plural = "Тренировки"
        indexes = [
            models.Index(fields=["user", "-date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.get_training_type_display()}"


class ForceMajeure(models.Model):
    """Форс-мажорные обстоятельства."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="force_majeures"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    reason = models.CharField(max_length=200, verbose_name="Причина")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Форс-мажор"
        verbose_name_plural = "Форс-мажоры"

    def __str__(self):
        return f"{self.user.username} - {self.start_date}: {self.reason}"
