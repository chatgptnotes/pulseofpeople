"""
News Article URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.news import NewsArticleViewSet

router = DefaultRouter()
router.register(r'', NewsArticleViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
]
