from django.urls import path
from .views import BlogViewsAPIView, TopAPIView, PerformanceAPIView

urlpatterns = [
    path('blog-views/', BlogViewsAPIView.as_view(), name='blog-views'),
    path('top/', TopAPIView.as_view(), name='top'),
    path('performance/', PerformanceAPIView.as_view(), name='performance'),
]
