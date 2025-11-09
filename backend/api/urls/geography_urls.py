"""
URL Configuration for Geography APIs (Wards and Polling Booths)
"""

from django.urls import path
from api.views.geography import wards, polling_booths

urlpatterns = [
    # ====================
    # WARDS ENDPOINTS
    # ====================

    # List and Create
    path('wards/', wards.ward_list_create, name='ward-list-create'),

    # Detail (Retrieve, Update, Delete)
    path('wards/<uuid:ward_id>/', wards.ward_detail, name='ward-detail'),

    # Bulk Import
    path('wards/bulk-import/', wards.ward_bulk_import, name='ward-bulk-import'),

    # Import Status
    path('wards/bulk-import/<uuid:job_id>/status/', wards.ward_import_status, name='ward-import-status'),

    # Statistics
    path('wards/statistics/', wards.ward_statistics, name='ward-statistics'),

    # ====================
    # POLLING BOOTHS ENDPOINTS
    # ====================

    # List and Create
    path('polling-booths/', polling_booths.polling_booth_list_create, name='polling-booth-list-create'),

    # Detail (Retrieve, Update, Delete)
    path('polling-booths/<uuid:booth_id>/', polling_booths.polling_booth_detail, name='polling-booth-detail'),

    # Bulk Import
    path('polling-booths/bulk-import/', polling_booths.polling_booth_bulk_import, name='polling-booth-bulk-import'),

    # Import Status
    path('polling-booths/bulk-import/<uuid:job_id>/status/', polling_booths.polling_booth_import_status, name='polling-booth-import-status'),

    # Statistics
    path('polling-booths/statistics/', polling_booths.polling_booth_statistics, name='polling-booth-statistics'),

    # Find Nearby
    path('polling-booths/nearby/', polling_booths.polling_booths_near, name='polling-booths-near'),
]
