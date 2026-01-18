from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"tags", views.TagViewSet, basename="tags")
router.register(r"areas", views.AreaViewSet, basename="areas")
router.register(r"sources", views.SourceViewSet, basename="sources")
router.register(r"nodes", views.InformationNodeViewSet, basename="nodes")
router.register(r"links", views.NodeLinkViewSet, basename="links")
router.register(r"projects", views.ProjectViewSet, basename="projects")
router.register(
    r"processing-sessions", views.ProcessingSessionViewSet, basename="processing"
)
# router.register(r'templates', views.TemplateViewSet, basename="templates")
router.register(r"daily-reviews", views.DailyReviewViewSet, basename="daily")
# router.register(r'import-jobs', views.ImportJobViewSet, basename="imports")
# router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path("", include(router.urls)),
]
