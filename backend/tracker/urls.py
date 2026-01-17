from django.urls import path
from . import views

urlpatterns = [
    # Нормативы
    # path('targets/', views.ActiveTargetsView.as_view(), name='targets'),
    
    # Ежедневные метрики
    path('metrics/update/', views.DailyMetricUpdateView.as_view(), name='metrics-update'),
    path('metrics/today/', views.DailyMetricTodayView.as_view(), name='metrics-today'),
    # path('metrics/<str:date_str>/', views.DailyMetricByDateView.as_view(), name='metrics-by-date'),
    # path('metrics/period/', views.DailyMetricPeriodView.as_view(), name='metrics-period'),
    
    # Замеры тела
    # path('body/', views.BodyMeasurementListView.as_view(), name='body-list'),
    # path('body/latest/', views.BodyMeasurementLatestView.as_view(), name='body-latest'),
    # path('body/<str:date_str>/', views.BodyMeasurementByDateView.as_view(), name='body-by-date'),
    # path('body/create/', views.BodyMeasurementCreateView.as_view(), name='body-create'),
    
    # Тренировки
    # path('trainings/today/', views.TrainingSessionTodayView.as_view(), name='trainings-today'),
    # path('trainings/<str:date_str>/', views.TrainingSessionByDateView.as_view(), name='trainings-by-date'),
    # path('trainings/create/', views.TrainingSessionCreateView.as_view(), name='trainings-create'),
    
    # Оценки
    # path('grade/<str:date_str>/', views.GradeByDateView.as_view(), name='grade-by-date'),
    # path('grade/period/', views.GradePeriodView.as_view(), name='grade-period'),
    
    # Дашборд
    path('dashboard/today/', views.DashboardTodayView.as_view(), name='dashboard-today'),
    
    # Аналитика
    path('analytics/trend/<str:metric_code>/', views.AnalyticsTrendView.as_view(), name='analytics-trend'),
    # path('analytics/streaks/', views.AnalyticsStreaksView.as_view(), name='analytics-streaks'),
]
