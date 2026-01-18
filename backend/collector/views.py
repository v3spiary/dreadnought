from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework import filters, parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from .serializers import *


@extend_schema(tags=["Collector"])
class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["parent"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        tag = self.get_object()
        children = tag.children.all()
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Collector"])
class AreaViewSet(viewsets.ModelViewSet):
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["priority"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return Area.objects.filter(user=self.request.user)

    @action(detail=True, methods=["get"])
    def nodes(self, request, pk=None):
        area = self.get_object()
        nodes = area.nodes.all()
        serializer = InformationNodeListSerializer(
            nodes, many=True, context={"request": request}
        )
        return Response(serializer.data)


@extend_schema(tags=["Collector"])
class SourceViewSet(viewsets.ModelViewSet):
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    parser_classes = [parsers.MultiPartParser]
    filterset_fields = ["source_type"]
    search_fields = ["title", "description", "url"]
    ordering_fields = ["captured_at", "title"]

    def get_queryset(self):
        return Source.objects.filter(user=self.request.user)

    # @action(detail=False, methods=['post'])
    # def bulk_create(self, request):
    #     """Массовое создание источников"""
    #     serializer = self.get_serializer(data=request.data.get('sources', []), many=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def nodes(self, request, pk=None):
        source = self.get_object()
        nodes = source.nodes.all()
        serializer = InformationNodeListSerializer(
            nodes, many=True, context={"request": request}
        )
        return Response(serializer.data)


@extend_schema(tags=["Collector"])
class InformationNodeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["stage", "node_type", "tags", "areas"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at", "atomicity_score", "clarity_score"]

    def get_queryset(self):
        return InformationNode.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return InformationNodeListSerializer
        return InformationNodeDetailSerializer

    @action(detail=False, methods=["get"])
    def inbox(self, request):
        """Узлы на этапе 'Захвачено' (Inbox)"""
        queryset = self.get_queryset().filter(stage="CAPTURED")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def for_review(self, request):
        """Узлы для повторения (интерливинг)"""
        # Узлы, которые не просматривались более 7 дней
        week_ago = timezone.now() - timedelta(days=7)
        queryset = (
            self.get_queryset()
            .filter(
                Q(last_reviewed__isnull=True) | Q(last_reviewed__lt=week_ago),
                stage__in=["ORGANIZED", "DISTILLED"],
            )
            .order_by("last_reviewed")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def advance_stage(self, request, pk=None):
        """Переход узла на следующий этап"""
        node = self.get_object()
        current_stage = node.stage
        stages = ["CAPTURED", "ORGANIZED", "DISTILLED", "EXPRESSED", "ARCHIVED"]

        try:
            current_index = stages.index(current_stage)
            if current_index < len(stages) - 1:
                node.stage = stages[current_index + 1]
                node.save()

                # Создаем запись о сессии обработки
                ProcessingSession.objects.create(
                    user=request.user,
                    node=node,
                    previous_stage=current_stage,
                    new_stage=node.stage,
                    time_spent=request.data.get("time_spent", 0),
                    actions_taken=request.data.get("actions_taken", []),
                    insights_gained=request.data.get("insights_gained", ""),
                )

                serializer = self.get_serializer(node)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Узел уже на последнем этапе"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"error": "Неизвестный этап"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["get"])
    def links(self, request, pk=None):
        """Получение всех связей узла"""
        node = self.get_object()
        outgoing = NodeLink.objects.filter(from_node=node)
        incoming = NodeLink.objects.filter(to_node=node)

        result = {
            "outgoing": NodeLinkSerializer(outgoing, many=True).data,
            "incoming": NodeLinkSerializer(incoming, many=True).data,
        }
        return Response(result)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """Запись повторения узла"""
        node = self.get_object()

        # Создаем или получаем ежедневный обзор
        daily_review, created = DailyReview.objects.get_or_create(
            user=request.user, date=timezone.now().date(), defaults={"insights": ""}
        )

        # Создаем запись о повторении
        node_review = NodeReview.objects.create(
            review=daily_review,
            node=node,
            recall_score=request.data.get("recall_score", 3),
            new_connections=request.data.get("new_connections", ""),
        )

        # Обновляем дату последнего повторения узла
        node.last_reviewed = timezone.now()
        node.save()

        return Response(NodeReviewSerializer(node_review).data)

    @action(detail=True, methods=["post"])
    def connect(self, request, pk=None):
        """Создание связи между узлами"""
        node = self.get_object()
        target_id = request.data.get("target_node")
        link_type = request.data.get("link_type", "RELATES")

        try:
            target_node = InformationNode.objects.get(id=target_id, user=request.user)

            # Проверяем, не существует ли уже такой связи
            existing_link = NodeLink.objects.filter(
                from_node=node, to_node=target_node, link_type=link_type
            ).first()

            if existing_link:
                return Response(
                    {"error": "Связь уже существует"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            link = NodeLink.objects.create(
                from_node=node,
                to_node=target_node,
                link_type=link_type,
                strength=request.data.get("strength", 1),
                description=request.data.get("description", ""),
            )

            return Response(NodeLinkSerializer(link).data)
        except InformationNode.DoesNotExist:
            return Response(
                {"error": "Целевой узел не найден"}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=["Collector"])
class NodeLinkViewSet(viewsets.ModelViewSet):
    serializer_class = NodeLinkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["link_type", "from_node", "to_node"]

    def get_queryset(self):
        # Возвращаем только связи между своими узлами
        return NodeLink.objects.filter(
            from_node__user=self.request.user, to_node__user=self.request.user
        )

    def create(self, request, *args, **kwargs):
        # Переопределяем для проверки принадлежности узлов
        from_node_id = request.data.get("from_node")
        to_node_id = request.data.get("to_node")

        try:
            from_node = InformationNode.objects.get(id=from_node_id, user=request.user)
            to_node = InformationNode.objects.get(id=to_node_id, user=request.user)
        except InformationNode.DoesNotExist:
            return Response(
                {"error": "Один из узлов не найден или не принадлежит вам"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверяем существование связи
        if NodeLink.objects.filter(
            from_node=from_node,
            to_node=to_node,
            link_type=request.data.get("link_type"),
        ).exists():
            return Response(
                {"error": "Связь уже существует"}, status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)


@extend_schema(tags=["Collector"])
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "areas"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "deadline"]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    @action(detail=True, methods=["get"])
    def nodes(self, request, pk=None):
        """Получение всех узлов проекта"""
        project = self.get_object()
        # Получаем узлы через промежуточную модель
        contributions = ProjectContribution.objects.filter(project=project)
        nodes = [contribution.node for contribution in contributions]

        serializer = InformationNodeListSerializer(
            nodes, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_node(self, request, pk=None):
        """Добавление узла в проект"""
        project = self.get_object()
        node_id = request.data.get("node_id")

        try:
            node = InformationNode.objects.get(id=node_id, user=request.user)

            # Создаем связь
            contribution, created = ProjectContribution.objects.get_or_create(
                project=project,
                node=node,
                defaults={
                    "role": request.data.get("role", "Материал"),
                    "importance": request.data.get("importance", 3),
                },
            )

            # Если узел добавлен в проект, переводим его на этап EXPRESSED
            if node.stage != "EXPRESSED":
                node.stage = "EXPRESSED"
                node.save()

            return Response(ProjectContributionSerializer(contribution).data)
        except InformationNode.DoesNotExist:
            return Response(
                {"error": "Узел не найден"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Активные проекты"""
        queryset = self.get_queryset().filter(status="ACTIVE")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Collector"])
class ProcessingSessionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProcessingSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["node", "new_stage", "previous_stage"]
    ordering_fields = ["created_at", "time_spent"]

    def get_queryset(self):
        return ProcessingSession.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def daily_summary(self, request):
        """Суммарное время обработки по дням"""
        from django.db.models.functions import TruncDate

        # Получаем данные за последние 30 дней
        thirty_days_ago = timezone.now() - timedelta(days=30)

        summary = (
            ProcessingSession.objects.filter(
                user=request.user, created_at__gte=thirty_days_ago
            )
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total_time=Sum("time_spent"), sessions_count=Count("id"))
            .order_by("-date")
        )

        return Response(summary)


# @extend_schema(tags=["Collector"])
# class TemplateViewSet(viewsets.ModelViewSet):
#     serializer_class = TemplateSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = ['template_type']
#     search_fields = ['name']

#     def get_queryset(self):
#         return Template.objects.filter(user=self.request.user)

#     @action(detail=True, methods=['post'])
#     def apply(self, request, pk=None):
#         """Применение шаблона для создания узла"""
#         template = self.get_object()

#         # Создаем новый узел на основе шаблона
#         node_data = {
#             'title': request.data.get('title', 'Новый узел'),
#             'content': self._fill_template(template, request.data),
#             'user': request.user
#         }

#         node = InformationNode.objects.create(**node_data)

#         # Применяем теги по умолчанию
#         if template.default_tags.exists():
#             node.tags.set(template.default_tags.all())

#         # Применяем область по умолчанию
#         if template.default_area:
#             AreaMembership.objects.create(
#                 node=node,
#                 area=template.default_area,
#                 relevance=3
#             )

#         serializer = InformationNodeDetailSerializer(node, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def _fill_template(self, template, data):
#         """Заполнение шаблона данными"""
#         structure = template.structure
#         content = ""

#         for field in structure.get('fields', []):
#             field_name = field.get('name')
#             field_value = data.get(field_name, '')

#             if field.get('type') == 'list' and isinstance(field_value, list):
#                 field_value = '\n'.join([f'- {item}' for item in field_value])

#             content += f"**{field_name.capitalize()}**: {field_value}\n\n"

#         return content


@extend_schema(tags=["Collector"])
class DailyReviewViewSet(viewsets.ModelViewSet):
    serializer_class = DailyReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["completed", "date"]
    ordering_fields = ["date"]

    def get_queryset(self):
        return DailyReview.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Завершение ежедневного обзора"""
        review = self.get_object()
        review.completed = True
        review.insights = request.data.get("insights", review.insights)
        review.save()

        return Response(self.get_serializer(review).data)

    @action(detail=True, methods=["post"])
    def add_review(self, request, pk=None):
        """Добавление повторения узла в обзор"""
        review = self.get_object()
        node_id = request.data.get("node_id")
        recall_score = request.data.get("recall_score", 3)

        try:
            node = InformationNode.objects.get(id=node_id, user=request.user)

            # Проверяем, не повторяли ли уже сегодня этот узел
            existing_review = NodeReview.objects.filter(
                review=review, node=node
            ).first()

            if existing_review:
                return Response(
                    {"error": "Этот узел уже повторен сегодня"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            node_review = NodeReview.objects.create(
                review=review,
                node=node,
                recall_score=recall_score,
                new_connections=request.data.get("new_connections", ""),
            )

            # Обновляем дату последнего повторения узла
            node.last_reviewed = timezone.now()
            node.save()

            return Response(NodeReviewSerializer(node_review).data)
        except InformationNode.DoesNotExist:
            return Response(
                {"error": "Узел не найден"}, status=status.HTTP_404_NOT_FOUND
            )


# @extend_schema(tags=["Collector"])
# class ImportJobViewSet(viewsets.ModelViewSet):
#     serializer_class = ImportJobSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['source_type', 'status']
#     ordering_fields = ['created_at', 'completed_at']

#     def get_queryset(self):
#         return ImportJob.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         """Запуск задачи импорта после создания"""
#         import_job = serializer.save(user=self.request.user)

#         # В реальном проекте здесь должен быть асинхронный таск (Celery, RQ)
#         # Здесь упрощенный вариант
#         self._process_import(import_job)

#     def _process_import(self, import_job):
#         """Обработка импорта (заглушка)"""
#         # В реальном проекте здесь парсинг файла и создание Source объектов
#         import_job.status = 'PROCESSING'
#         import_job.save()

#         # Имитация обработки
#         import time
#         time.sleep(2)

#         import_job.status = 'COMPLETED'
#         import_job.items_processed = 10
#         import_job.items_total = 10
#         import_job.completed_at = timezone.now()
#         import_job.save()


# @extend_schema(tags=["Collector"])
# class DashboardViewSet(viewsets.ViewSet):
#     # permission_classes = [IsAuthenticated]

#     @action(detail=False, methods=['get'])
#     def statistics(self, request):
#         """Получение статистики по всем данным"""
#         user = request.user

#         # Базовые статистики
#         stats = {
#             'total_nodes': InformationNode.objects.filter(user=user).count(),
#             'nodes_by_stage': dict(InformationNode.objects
#                 .filter(user=user)
#                 .values_list('stage')
#                 .annotate(count=Count('id'))
#                 .order_by('stage')),
#             'nodes_by_type': dict(InformationNode.objects
#                 .filter(user=user)
#                 .values_list('node_type')
#                 .annotate(count=Count('id'))
#                 .order_by('node_type')),
#             'total_sources': Source.objects.filter(user=user).count(),
#             'total_links': NodeLink.objects.filter(
#                 from_node__user=user,
#                 to_node__user=user
#             ).count(),
#             'total_projects': Project.objects.filter(user=user).count(),
#         }

#         # Время обработки
#         today = timezone.now().date()
#         week_ago = timezone.now() - timedelta(days=7)

#         stats['daily_processing_time'] = ProcessingSession.objects.filter(
#             user=user,
#             created_at__date=today
#         ).aggregate(total=Sum('time_spent'))['total'] or 0

#         stats['weekly_processing_time'] = ProcessingSession.objects.filter(
#             user=user,
#             created_at__gte=week_ago
#         ).aggregate(total=Sum('time_spent'))['total'] or 0

#         # Самые используемые теги
#         from django.db.models import Count
#         stats['most_used_tags'] = list(
#             Tag.objects.filter(user=user)
#             .annotate(usage_count=Count('nodes'))
#             .order_by('-usage_count')[:10]
#             .values('id', 'name', 'color', 'usage_count')
#         )

#         return Response(stats)

#     @action(detail=False, methods=['get'])
#     def recent_activity(self, request):
#         """Последние активности"""
#         user = request.user

#         # Последние сессии обработки
#         recent_sessions = ProcessingSession.objects.filter(
#             user=user
#         ).order_by('-created_at')[:10]

#         # Последние созданные узлы
#         recent_nodes = InformationNode.objects.filter(
#             user=user
#         ).order_by('-created_at')[:10]

#         # Последние обзоры
#         recent_reviews = DailyReview.objects.filter(
#             user=user
#         ).order_by('-date')[:5]

#         return Response({
#             'recent_sessions': ProcessingSessionSerializer(
#                 recent_sessions, many=True, context={'request': request}
#             ).data,
#             'recent_nodes': InformationNodeListSerializer(
#                 recent_nodes, many=True, context={'request': request}
#             ).data,
#             'recent_reviews': DailyReviewSerializer(
#                 recent_reviews, many=True, context={'request': request}
#             ).data,
#         })

#     @action(detail=False, methods=['get'])
#     def knowledge_graph(self, request):
#         """Граф знаний (первые 50 узлов)"""
#         user = request.user

#         nodes = InformationNode.objects.filter(user=user)[:50]
#         links = NodeLink.objects.filter(
#             from_node__in=nodes,
#             to_node__in=nodes
#         )

#         node_data = []
#         for node in nodes:
#             node_data.append({
#                 'id': node.id,
#                 'title': node.title,
#                 'stage': node.stage,
#                 'stage_display': node.get_stage_display(),
#                 'type': node.node_type,
#                 'type_display': node.get_node_type_display(),
#             })

#         link_data = []
#         for link in links:
#             link_data.append({
#                 'source': link.from_node_id,
#                 'target': link.to_node_id,
#                 'type': link.link_type,
#                 'type_display': link.get_link_type_display(),
#                 'strength': link.strength,
#             })

#         return Response({
#             'nodes': node_data,
#             'links': link_data
#         })
