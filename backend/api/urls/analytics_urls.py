"""
Analytics and Reporting URL Configuration
"""

from django.urls import path
from api.views.analytics import (
    VoterAnalyticsView,
    CampaignAnalyticsView,
    InteractionAnalyticsView,
    GeographicAnalyticsView,
    SentimentAnalyticsView,
    SocialMediaAnalyticsView,
    FieldReportAnalyticsView,
    BoothAnalyticsView,
    ComparativeAnalyticsView,
    PredictiveAnalyticsView,
)
from api.views.reports import (
    ExecutiveSummaryReportView,
    CampaignPerformanceReportView,
    ConstituencyReportView,
    DailyActivityReportView,
    WeeklySummaryReportView,
    VolunteerPerformanceReportView,
    CustomReportBuilderView,
    ReportStatusView,
    ReportDownloadView,
    ReportTemplateListView,
    ReportTemplateDetailView,
    ScheduledReportsView,
)
from api.views.export import (
    ExportView,
    ExportStatusView,
    ExportDownloadView,
    QuickExportCSVView,
    QuickExportJSONView,
    ExportTemplateView,
)

urlpatterns = [
    # Analytics Endpoints
    path('analytics/voters/', VoterAnalyticsView.as_view(), name='analytics-voters'),
    path('analytics/campaigns/', CampaignAnalyticsView.as_view(), name='analytics-campaigns'),
    path('analytics/interactions/', InteractionAnalyticsView.as_view(), name='analytics-interactions'),
    path('analytics/geographic/', GeographicAnalyticsView.as_view(), name='analytics-geographic'),
    path('analytics/sentiment/', SentimentAnalyticsView.as_view(), name='analytics-sentiment'),
    path('analytics/social-media/', SocialMediaAnalyticsView.as_view(), name='analytics-social-media'),
    path('analytics/field-reports/', FieldReportAnalyticsView.as_view(), name='analytics-field-reports'),
    path('analytics/polling-booths/', BoothAnalyticsView.as_view(), name='analytics-booths'),
    path('analytics/compare/', ComparativeAnalyticsView.as_view(), name='analytics-compare'),
    path('analytics/predictions/', PredictiveAnalyticsView.as_view(), name='analytics-predictions'),

    # Report Generation
    path('reports/executive-summary/', ExecutiveSummaryReportView.as_view(), name='report-executive-summary'),
    path('reports/campaign-performance/', CampaignPerformanceReportView.as_view(), name='report-campaign-performance'),
    path('reports/constituency/', ConstituencyReportView.as_view(), name='report-constituency'),
    path('reports/daily-activity/', DailyActivityReportView.as_view(), name='report-daily-activity'),
    path('reports/weekly-summary/', WeeklySummaryReportView.as_view(), name='report-weekly-summary'),
    path('reports/volunteer-performance/', VolunteerPerformanceReportView.as_view(), name='report-volunteer-performance'),
    path('reports/custom/', CustomReportBuilderView.as_view(), name='report-custom'),

    # Report Status and Download
    path('reports/<uuid:report_id>/status/', ReportStatusView.as_view(), name='report-status'),
    path('reports/<uuid:report_id>/download/', ReportDownloadView.as_view(), name='report-download'),

    # Report Templates
    path('reports/templates/', ReportTemplateListView.as_view(), name='report-templates'),
    path('reports/templates/<uuid:template_id>/', ReportTemplateDetailView.as_view(), name='report-template-detail'),
    path('reports/scheduled/', ScheduledReportsView.as_view(), name='scheduled-reports'),

    # Export API
    path('export/', ExportView.as_view(), name='export'),
    path('export/<uuid:job_id>/status/', ExportStatusView.as_view(), name='export-status'),
    path('export/<uuid:job_id>/download/', ExportDownloadView.as_view(), name='export-download'),

    # Quick Exports (synchronous, limited)
    path('export/quick/csv/<str:resource>/', QuickExportCSVView.as_view(), name='quick-export-csv'),
    path('export/quick/json/<str:resource>/', QuickExportJSONView.as_view(), name='quick-export-json'),
    path('export/template/<str:resource>/', ExportTemplateView.as_view(), name='export-template'),
]
