from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
        read_only_fields = ("id",)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "token",
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class TagSerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "description",
            "parent",
            "children_count",
            "user",
        )
        read_only_fields = ("user", "children_count")

    def get_children_count(self, obj):
        return obj.children.count()

    def validate(self, data):
        # Проверяем, что родительский тег принадлежит тому же пользователю
        request = self.context.get("request")
        if request and request.user:
            parent = data.get("parent")
            if parent and parent.user != request.user:
                raise serializers.ValidationError(
                    "Родительский тег должен принадлежать вам"
                )
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class AreaSerializer(serializers.ModelSerializer):
    nodes_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "color",
            "nodes_count",
            "projects_count",
            "user",
        )
        read_only_fields = ("user", "nodes_count", "projects_count")

    def get_nodes_count(self, obj):
        return obj.nodes.count()

    def get_projects_count(self, obj):
        return obj.projects.count()

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class SourceSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source="get_source_type_display", read_only=True
    )
    nodes_count = serializers.SerializerMethodField()

    class Meta:
        model = Source
        fields = (
            "id",
            "title",
            "url",
            "source_type",
            "type_display",
            "description",
            "captured_at",
            "raw_content",
            "metadata",
            "nodes_count",
            "user",
            "source_file",
        )
        read_only_fields = ("user", "captured_at", "nodes_count")

    def get_nodes_count(self, obj):
        return obj.nodes.count()

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class InformationNodeListSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    type_display = serializers.CharField(source="get_node_type_display", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    areas = AreaSerializer(many=True, read_only=True)
    incoming_links_count = serializers.SerializerMethodField()
    outgoing_links_count = serializers.SerializerMethodField()

    class Meta:
        model = InformationNode
        fields = (
            "id",
            "title",
            "stage",
            "stage_display",
            "node_type",
            "type_display",
            "atomicity_score",
            "clarity_score",
            "tags",
            "areas",
            "created_at",
            "updated_at",
            "last_reviewed",
            "incoming_links_count",
            "outgoing_links_count",
            "user",
        )
        read_only_fields = ("user", "created_at", "updated_at")

    def get_incoming_links_count(self, obj):
        return obj.incoming_links.count()

    def get_outgoing_links_count(self, obj):
        return obj.outgoing_links.count()


class InformationNodeDetailSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    type_display = serializers.CharField(source="get_node_type_display", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    areas = AreaSerializer(many=True, read_only=True)
    sources = SourceSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True,
        source="tags",
        required=False,
    )
    area_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Area.objects.all(),
        write_only=True,
        source="areas",
        required=False,
    )
    source_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Source.objects.all(),
        write_only=True,
        source="sources",
        required=False,
    )

    class Meta:
        model = InformationNode
        fields = (
            "id",
            "title",
            "content",
            "stage",
            "stage_display",
            "node_type",
            "type_display",
            "atomicity_score",
            "clarity_score",
            "tags",
            "areas",
            "sources",
            "tag_ids",
            "area_ids",
            "source_ids",
            "created_at",
            "updated_at",
            "last_reviewed",
            "user",
        )
        read_only_fields = ("user", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class NodeLinkSerializer(serializers.ModelSerializer):
    from_node_title = serializers.CharField(source="from_node.title", read_only=True)
    to_node_title = serializers.CharField(source="to_node.title", read_only=True)
    link_type_display = serializers.CharField(
        source="get_link_type_display", read_only=True
    )

    class Meta:
        model = NodeLink
        fields = (
            "id",
            "from_node",
            "from_node_title",
            "to_node",
            "to_node_title",
            "link_type",
            "link_type_display",
            "strength",
            "description",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def validate(self, data):
        # Проверяем, что узлы принадлежат тому же пользователю
        request = self.context.get("request")
        if request and request.user:
            from_node = data.get("from_node")
            to_node = data.get("to_node")

            if from_node and from_node.user != request.user:
                raise serializers.ValidationError(
                    "Исходный узел должен принадлежать вам"
                )
            if to_node and to_node.user != request.user:
                raise serializers.ValidationError(
                    "Целевой узел должен принадлежать вам"
                )

            # Проверяем, что это не циклическая ссылка
            if from_node and to_node and from_node.id == to_node.id:
                raise serializers.ValidationError(
                    "Нельзя создавать ссылку узла на самого себя"
                )

        return data


class ProjectSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    areas = AreaSerializer(many=True, read_only=True)
    nodes_count = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "description",
            "status",
            "status_display",
            "deadline",
            "tags",
            "areas",
            "nodes_count",
            "days_until_deadline",
            "is_overdue",
            "created_at",
            "updated_at",
            "user",
        )
        read_only_fields = ("user", "created_at", "updated_at", "nodes_count")

    def get_nodes_count(self, obj):
        return obj.informationnode_set.count()

    def get_days_until_deadline(self, obj):
        if obj.deadline:
            from datetime import date

            today = date.today()
            delta = obj.deadline - today
            return delta.days
        return None

    def get_is_overdue(self, obj):
        if obj.deadline:
            from datetime import date

            today = date.today()
            return today > obj.deadline
        return False

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ProcessingSessionSerializer(serializers.ModelSerializer):
    node_title = serializers.CharField(source="node.title", read_only=True)
    previous_stage_display = serializers.CharField(
        source="get_previous_stage_display", read_only=True
    )
    new_stage_display = serializers.CharField(
        source="get_new_stage_display", read_only=True
    )

    class Meta:
        model = ProcessingSession
        fields = (
            "id",
            "node",
            "node_title",
            "previous_stage",
            "previous_stage_display",
            "new_stage",
            "new_stage_display",
            "actions_taken",
            "time_spent",
            "insights_gained",
            "created_at",
            "user",
        )
        read_only_fields = ("user", "created_at")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ProjectContributionSerializer(serializers.ModelSerializer):
    node_title = serializers.CharField(source="node.title", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = ProjectContribution
        fields = (
            "id",
            "node",
            "node_title",
            "project",
            "project_title",
            "role",
            "importance",
            "added_at",
        )
        read_only_fields = ("added_at",)


# class TemplateSerializer(serializers.ModelSerializer):
#     type_display = serializers.CharField(source='get_template_type_display', read_only=True)
#     default_tags = TagSerializer(many=True, read_only=True)
#     default_area_name = serializers.CharField(source='default_area.name', read_only=True)
#     tag_ids = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=Tag.objects.all(),
#         write_only=True,
#         source='default_tags',
#         required=False
#     )

#     class Meta:
#         model = Template
#         fields = ('id', 'name', 'template_type', 'type_display', 'structure',
#                  'default_tags', 'default_area', 'default_area_name',
#                  'tag_ids', 'user')
#         read_only_fields = ('user',)

#     def create(self, validated_data):
#         validated_data['user'] = self.context['request'].user
#         return super().create(validated_data)


class DailyReviewSerializer(serializers.ModelSerializer):
    nodes_reviewed_count = serializers.SerializerMethodField()
    average_recall_score = serializers.SerializerMethodField()

    class Meta:
        model = DailyReview
        fields = (
            "id",
            "date",
            "insights",
            "completed",
            "nodes_reviewed_count",
            "average_recall_score",
            "user",
        )
        read_only_fields = ("user", "nodes_reviewed_count", "average_recall_score")

    def get_nodes_reviewed_count(self, obj):
        return obj.nodereview_set.count()

    def get_average_recall_score(self, obj):
        from django.db.models import Avg

        avg = obj.nodereview_set.aggregate(Avg("recall_score"))
        return avg["recall_score__avg"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class NodeReviewSerializer(serializers.ModelSerializer):
    node_title = serializers.CharField(source="node.title", read_only=True)
    recall_score_display = serializers.CharField(
        source="get_recall_score_display", read_only=True
    )

    class Meta:
        model = NodeReview
        fields = (
            "id",
            "review",
            "node",
            "node_title",
            "recall_score",
            "recall_score_display",
            "new_connections",
            "reviewed_at",
        )
        read_only_fields = ("reviewed_at",)


# class ImportJobSerializer(serializers.ModelSerializer):
#     type_display = serializers.CharField(source='get_source_type_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     progress_percentage = serializers.SerializerMethodField()
#     duration_seconds = serializers.SerializerMethodField()

#     class Meta:
#         model = ImportJob
#         fields = ('id', 'source_type', 'type_display', 'source_file',
#                  'status', 'status_display', 'items_processed', 'items_total',
#                  'errors', 'progress_percentage', 'duration_seconds',
#                  'created_at', 'completed_at', 'user')
#         read_only_fields = ('user', 'created_at', 'completed_at', 'errors',
#                           'items_processed', 'items_total', 'status')

#     def get_progress_percentage(self, obj):
#         if obj.items_total > 0:
#             return (obj.items_processed / obj.items_total) * 100
#         return 0

#     def get_duration_seconds(self, obj):
#         if obj.completed_at and obj.created_at:
#             return (obj.completed_at - obj.created_at).total_seconds()
#         return None

#     def create(self, validated_data):
#         validated_data['user'] = self.context['request'].user
#         return super().create(validated_data)


class DashboardMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetric
        fields = ("id", "metric_type", "value", "recorded_at", "metadata", "user")
        read_only_fields = ("user", "recorded_at")


class NodeGraphSerializer(serializers.Serializer):
    """Сериализатор для графа связей между узлами"""

    nodes = serializers.ListField(child=serializers.DictField())
    links = serializers.ListField(child=serializers.DictField())


class StatisticsSerializer(serializers.Serializer):
    """Сериализатор для статистики"""

    total_nodes = serializers.IntegerField()
    nodes_by_stage = serializers.DictField()
    nodes_by_type = serializers.DictField()
    total_sources = serializers.IntegerField()
    total_links = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    daily_processing_time = serializers.IntegerField()
    weekly_processing_time = serializers.IntegerField()
    most_used_tags = serializers.ListField(child=serializers.DictField())
