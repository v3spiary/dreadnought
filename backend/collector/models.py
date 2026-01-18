from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from config.storage import MediaMinIOStorage


class Source(models.Model):
    """Модель для источников информации"""

    SOURCE_TYPES = [
        ("WEB", "Веб-страница"),
        ("YOUTUBE", "YouTube"),
        ("BOOK", "Книга"),
        ("ARTICLE", "Научная статья"),
        ("MICROSCOPE", "Наблюдение под микроскопом"),
        ("COURSE", "Курс/лекция"),
        ("IDEA", "Собственная идея"),
        ("OTHER", "Другое"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sources",
        verbose_name="Пользователь",
    )
    title = models.CharField("Название", max_length=500)
    url = models.URLField("URL", max_length=2000, blank=True, null=True)
    source_type = models.CharField("Тип источника", max_length=20, choices=SOURCE_TYPES)
    description = models.TextField("Описание", blank=True)
    captured_at = models.DateTimeField("Дата сохранения", auto_now_add=True)
    raw_content = models.TextField("Исходный контент", blank=True)
    metadata = models.JSONField("Метаданные", default=dict, blank=True)

    source_file = models.FileField(
        "Файл для импорта",
        upload_to="info_sources/",
        storage=MediaMinIOStorage(),
        blank=True,
        null=True,
        max_length=500,
    )

    class Meta:
        verbose_name = "Источник информации"
        verbose_name_plural = "Источники информации"
        ordering = ["-captured_at"]

    def __str__(self):
        return f"{self.title} ({self.get_source_type_display()})"


class Tag(models.Model):
    """Гибкие теги для организации"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tags", verbose_name="Пользователь"
    )
    name = models.CharField("Название тега", max_length=100)
    color = models.CharField("Цвет", max_length=7, default="#808080")
    description = models.TextField("Описание", blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительский тег",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        unique_together = ["user", "name"]

    def __str__(self):
        return self.name


class Area(models.Model):
    """Область интересов/ответственности (парадигма PARA)"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="areas",
        verbose_name="Пользователь",
    )
    name = models.CharField("Название области", max_length=200)
    description = models.TextField("Описание", blank=True)
    priority = models.IntegerField("Приоритет", default=1)
    color = models.CharField("Цвет", max_length=7, default="#4CAF50")

    class Meta:
        verbose_name = "Область знаний"
        verbose_name_plural = "Области знаний"

    def __str__(self):
        return self.name


class InformationNode(models.Model):
    """
    Основная единица информации - реализация принципов Zettelkasten
    Каждая заметка/идея/факт как отдельный узел в сети знаний
    """

    PROCESSING_STAGES = [
        ("CAPTURED", "Захвачено"),  # Этап 1: Сырая информация
        ("ORGANIZED", "Организовано"),  # Этап 2: Категоризировано
        ("DISTILLED", "Перегнано"),  # Этап 3: Осмыслено и переработано
        ("EXPRESSED", "Выражено"),  # Этап 4: Использовано в проекте
        ("ARCHIVED", "Архивировано"),  # Неактивная, но сохраненная
    ]

    NODE_TYPES = [
        ("ATOMIC", "Атомарная идея"),  # Одна законченная мысль
        ("CONCEPT", "Концепция"),  # Более сложное понятие
        ("OBSERVATION", "Наблюдение"),  # Научное наблюдение
        ("QUESTION", "Вопрос"),  # Вопрос для исследования
        ("HYPOTHESIS", "Гипотеза"),  # Научное предположение
        ("SUMMARY", "Резюме"),  # Сводка по теме
        ("PROJECT_NOTE", "Заметка проекта"),  # Связана с конкретным проектом
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="nodes",
        verbose_name="Пользователь",
    )
    title = models.CharField("Заголовок", max_length=500)
    content = models.TextField("Содержание")
    stage = models.CharField(
        "Этап обработки", max_length=20, choices=PROCESSING_STAGES, default="CAPTURED"
    )
    node_type = models.CharField(
        "Тип узла", max_length=20, choices=NODE_TYPES, default="ATOMIC"
    )
    atomicity_score = models.IntegerField(
        "Оценка атомарности",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Насколько атомарна идея (1 - сложная, 10 - простая и законченная)",
    )
    clarity_score = models.IntegerField(
        "Оценка ясности",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Насколько ясно изложено (1 - сыро, 10 - кристально понятно)",
    )

    # Связи с источниками
    sources = models.ManyToManyField(
        Source, related_name="nodes", blank=True, verbose_name="Источники"
    )
    tags = models.ManyToManyField(
        Tag, related_name="nodes", blank=True, verbose_name="Теги"
    )
    areas = models.ManyToManyField(
        Area,
        through="AreaMembership",
        related_name="nodes",
        blank=True,
        verbose_name="Области знаний",
    )

    # Технические поля
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    last_reviewed = models.DateTimeField("Последний обзор", null=True, blank=True)

    class Meta:
        verbose_name = "Информационный узел"
        verbose_name_plural = "Информационные узлы"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} [{self.get_stage_display()}]"


class NodeLink(models.Model):
    """Связи между узлами для создания сети знаний"""

    LINK_TYPES = [
        ("RELATES", "Относится к"),
        ("SUPPORTS", "Подтверждает"),
        ("CONTRADICTS", "Противоречит"),
        ("DEVELOPS", "Развивает"),
        ("ANSWERS", "Отвечает на"),
        ("CITES", "Цитирует"),
        ("EXAMPLE", "Пример для"),
        ("APPLICATION", "Применение"),
    ]

    from_node = models.ForeignKey(
        InformationNode,
        on_delete=models.CASCADE,
        related_name="outgoing_links",
        verbose_name="Исходный узел",
    )
    to_node = models.ForeignKey(
        InformationNode,
        on_delete=models.CASCADE,
        related_name="incoming_links",
        verbose_name="Целевой узел",
    )
    link_type = models.CharField("Тип связи", max_length=20, choices=LINK_TYPES)
    strength = models.IntegerField(
        "Сила связи",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Сила связи (1 - слабая, 5 - очень сильная)",
    )
    description = models.TextField("Описание связи", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Связь между узлами"
        verbose_name_plural = "Связи между узлами"
        unique_together = ["from_node", "to_node", "link_type"]

    def __str__(self):
        return f"{self.from_node} → {self.to_node} ({self.get_link_type_display()})"


class Project(models.Model):
    """Активный проект для этапа EXPRESS"""

    STATUS_CHOICES = [
        ("PLANNING", "Планирование"),
        ("ACTIVE", "Активный"),
        ("PAUSED", "Приостановлен"),
        ("COMPLETED", "Завершен"),
        ("ARCHIVED", "Архивирован"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Пользователь",
    )
    title = models.CharField("Название проекта", max_length=500)
    description = models.TextField("Описание")
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="PLANNING"
    )
    deadline = models.DateField("Дедлайн", null=True, blank=True)

    # Связи через промежуточные модели
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")
    areas = models.ManyToManyField(Area, blank=True, verbose_name="Области знаний")

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ProcessingSession(models.Model):
    """Сессия обработки информации - для отслеживания прогресса"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="processing_sessions",
        verbose_name="Пользователь",
    )
    node = models.ForeignKey(
        InformationNode,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Информационный узел",
    )

    previous_stage = models.CharField(
        "Предыдущий этап", max_length=20, choices=InformationNode.PROCESSING_STAGES
    )
    new_stage = models.CharField(
        "Новый этап", max_length=20, choices=InformationNode.PROCESSING_STAGES
    )

    # Что было сделано в этой сессии
    actions_taken = models.JSONField(
        "Выполненные действия",
        default=list,
        help_text="Список выполненных действий в формате JSON",
    )
    time_spent = models.IntegerField(
        "Затраченное время (мин)", help_text="Время в минутах, потраченное на обработку"
    )
    insights_gained = models.TextField("Полученные инсайты", blank=True)

    created_at = models.DateTimeField("Дата сессии", auto_now_add=True)

    class Meta:
        verbose_name = "Сессия обработки"
        verbose_name_plural = "Сессии обработки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Обработка {self.node.title} ({self.created_at.date()})"


class AreaMembership(models.Model):
    """Связь между узлами и областями с указанием релевантности"""

    node = models.ForeignKey(
        InformationNode, on_delete=models.CASCADE, verbose_name="Информационный узел"
    )
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE, verbose_name="Область знаний"
    )
    relevance = models.IntegerField(
        "Релевантность",
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Релевантность узла для области (1 - низкая, 5 - высокая)",
    )
    added_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Принадлежность к области"
        verbose_name_plural = "Принадлежности к областям"
        unique_together = ["node", "area"]


class ProjectContribution(models.Model):
    """Связь между узлами и проектами"""

    node = models.ForeignKey(
        InformationNode, on_delete=models.CASCADE, verbose_name="Информационный узел"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name="Проект"
    )
    role = models.CharField(
        "Роль узла", max_length=100, help_text="Как узел используется в проекте"
    )
    importance = models.IntegerField(
        "Важность",
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Важность узла для проекта (1 - низкая, 5 - критическая)",
    )
    added_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Вклад в проект"
        verbose_name_plural = "Вклады в проекты"
        unique_together = ["node", "project"]


# class Template(models.Model):
#     """Шаблоны для обработки информации"""
#     TEMPLATE_TYPES = [
#         ('SOURCE_PROCESSING', 'Обработка источника'),
#         ('NODE_CREATION', 'Создание узла'),
#         ('OBSERVATION', 'Наблюдение под микроскопом'),
#         ('RESEARCH_PAPER', 'Научная статья'),
#         ('LITERATURE_REVIEW', 'Обзор литературы'),
#     ]

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='templates',
#         verbose_name='Пользователь'
#     )
#     name = models.CharField('Название шаблона', max_length=200)
#     template_type = models.CharField(
#         'Тип шаблона',
#         max_length=50,
#         choices=TEMPLATE_TYPES
#     )
#     structure = models.JSONField(
#         'Структура шаблона',
#         default=dict,
#         help_text="Структура шаблона в формате JSON (поля, разделы)"
#     )
#     default_tags = models.ManyToManyField(
#         Tag,
#         blank=True,
#         verbose_name='Теги по умолчанию'
#     )
#     default_area = models.ForeignKey(
#         Area,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name='Область по умолчанию'
#     )

#     class Meta:
#         verbose_name = 'Шаблон'
#         verbose_name_plural = 'Шаблоны'

#     def __str__(self):
#         return f"{self.name} ({self.get_template_type_display()})"


class DailyReview(models.Model):
    """Ежедневный обзор для повторения и интерливинга"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    date = models.DateField("Дата обзора", default=timezone.now)

    insights = models.TextField("Инсайты дня", blank=True)
    completed = models.BooleanField("Завершено", default=False)

    class Meta:
        verbose_name = "Ежедневный обзор"
        verbose_name_plural = "Ежедневные обзоры"
        unique_together = ["user", "date"]

    def __str__(self):
        return f"Обзор {self.user.username} за {self.date}"


class NodeReview(models.Model):
    """Запись о повторении конкретного узла"""

    review = models.ForeignKey(
        DailyReview, on_delete=models.CASCADE, verbose_name="Ежедневный обзор"
    )
    node = models.ForeignKey(
        InformationNode, on_delete=models.CASCADE, verbose_name="Информационный узел"
    )

    RECALL_SCORES = [
        (1, "Не вспомнил"),
        (2, "С трудом вспомнил"),
        (3, "Вспомнил с подсказками"),
        (4, "Вспомнил легко"),
        (5, "Знаю отлично"),
    ]

    recall_score = models.IntegerField("Оценка вспоминания", choices=RECALL_SCORES)
    new_connections = models.TextField(
        "Новые связи", blank=True, help_text="Новые связи, возникшие при повторении"
    )
    reviewed_at = models.DateTimeField("Время повторения", auto_now_add=True)

    class Meta:
        verbose_name = "Повторение узла"
        verbose_name_plural = "Повторения узлов"
        unique_together = ["review", "node"]


# class ImportJob(models.Model):
#     """Задача импорта данных из внешних источников"""
#     SOURCE_TYPES = [
#         ('POCKET', 'Pocket'),
#         ('READWISE', 'Readwise'),
#         ('YOUTUBE', 'YouTube History'),
#         ('BOOKMARKS', 'Браузерные закладки'),
#         ('OBSIDIAN', 'Obsidian'),
#         ('NOTION', 'Notion'),
#     ]

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='import_jobs',
#         verbose_name='Пользователь'
#     )
#     source_type = models.CharField(
#         'Тип источника',
#         max_length=20,
#         choices=SOURCE_TYPES
#     )
#     source_file = models.FileField(
#         'Файл для импорта',
#         upload_to='imports/',
#         blank=True,
#         null=True
#     )
#     status = models.CharField('Статус', max_length=20, default='PENDING')
#     items_processed = models.IntegerField('Обработано элементов', default=0)
#     items_total = models.IntegerField('Всего элементов', default=0)
#     errors = models.JSONField('Ошибки', default=list, blank=True)
#     created_at = models.DateTimeField('Дата создания', auto_now_add=True)
#     completed_at = models.DateTimeField('Дата завершения', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Задача импорта'
#         verbose_name_plural = 'Задачи импорта'

#     def __str__(self):
#         return f"Импорт {self.get_source_type_display()} для {self.user}"


class DashboardMetric(models.Model):
    """Метрики для дашборда прогресса"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="Пользователь",
    )
    metric_type = models.CharField("Тип метрики", max_length=50)
    value = models.FloatField("Значение")
    recorded_at = models.DateTimeField("Время записи", auto_now_add=True)
    metadata = models.JSONField("Метаданные", default=dict, blank=True)

    class Meta:
        verbose_name = "Метрика дашборда"
        verbose_name_plural = "Метрики дашборда"

    def __str__(self):
        return f"{self.metric_type}: {self.value} ({self.recorded_at.date()})"
