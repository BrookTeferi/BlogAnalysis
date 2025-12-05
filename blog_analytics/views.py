"""
Analytics API Views (Senior-Level Implementation)
Provides aggregated metrics for blog views, top performers,
and time-series performance. Fully optimized and maintainable.
"""

import json
from typing import Optional, Tuple

from django.db.models import Count, Sum, Q, F, QuerySet
from django.http import QueryDict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import BlogView, Blog
from .serializers import BlogViewsSerializer, TopSerializer, PerformanceSerializer
from .filters import apply_filters
from .utils import (
    get_date_range,
    get_trunc_function,
    calculate_growth_percentage,
    format_period_label,
    validate_range,
    validate_compare,
    validate_object_type,
    validate_top_type,
)



def load_filters(filters_param: Optional[str]) -> Optional[dict]:
    if not filters_param:
        return None

    try:
        return json.loads(filters_param)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in filters parameter")


def guard(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def get_filters_and_range(request, allow_range: bool = True) -> Tuple[Optional[dict], Optional[Tuple]]:
    filters_param = request.query_params.get("filters")
    filter_dict = load_filters(filters_param)

    range_type = request.query_params.get("range") if allow_range else None

    if range_type:
        guard(
            validate_range(range_type),
            'range must be one of "month", "week", or "year".',
        )
        start, end = get_date_range(range_type)
        return filter_dict, (start, end)

    return filter_dict, None



class BlogViewsAPIView(APIView):

    @extend_schema(
        summary="Blog Views Grouping",
        description="Groups blog views by country or user.",
        parameters=[
            OpenApiParameter(
                name='object_type',
                type=OpenApiTypes.STR,
                required=True,
                enum=['country', 'user'],
                description='Group by country or user'
            ),
            OpenApiParameter(
                name='range',
                type=OpenApiTypes.STR,
                required=True,
                enum=['month', 'week', 'year'],
                description='Time range window'
            ),
            OpenApiParameter(
                name='filters',
                type=OpenApiTypes.STR,
                required=False,
                description='Dynamic JSON filter'
            ),
        ],
        responses={200: BlogViewsSerializer(many=True)},
        tags=["Analytics"],
    )
    def get(self, request):
        try:
            object_type = request.query_params.get("object_type")
            guard(object_type, "object_type is required")
            guard(validate_object_type(object_type), 'object_type must be "country" or "user"')

            # Load filters and range
            filter_dict, date_range = get_filters_and_range(request, allow_range=True)
            guard(date_range, "range parameter is required")

            start_date, end_date = date_range

            queryset = BlogView.objects.filter(
                viewed_at__gte=start_date,
                viewed_at__lte=end_date,
            )

            # Apply dynamic filters
            if filter_dict:
                queryset = apply_filters(queryset, filter_dict)

            # Group by object type
            if object_type == "country":
                results = queryset.values("country__name").annotate(
                    blog_count=Count("blog", distinct=True),
                    total_views=Count("id")
                ).filter(
                    country__name__isnull=False
                ).order_by("-total_views")

                data = [
                    {"x": r["country__name"], "y": r["blog_count"], "z": r["total_views"]}
                    for r in results
                ]

            else:  # user
                results = queryset.values("viewer__username").annotate(
                    blog_count=Count("blog", distinct=True),
                    total_views=Count("id"),
                ).filter(
                    viewer__username__isnull=False
                ).order_by("-total_views")

                data = [
                    {"x": r["viewer__username"], "y": r["blog_count"], "z": r["total_views"]}
                    for r in results
                ]

            return Response(BlogViewsSerializer(data, many=True).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopAPIView(APIView):

    @extend_schema(
        summary="Top 10 Rankings",
        description="Returns top 10 users/countries/blogs by views.",
        parameters=[
            OpenApiParameter(
                name='top',
                required=True,
                type=OpenApiTypes.STR,
                enum=['user', 'country', 'blog']
            ),
            OpenApiParameter(
                name='range',
                required=False,
                enum=['month', 'week', 'year']
            ),
            OpenApiParameter(
                name='filters',
                required=False,
                type=OpenApiTypes.STR
            ),
        ],
        responses={200: TopSerializer(many=True)},
        tags=["Analytics"],
    )
    def get(self, request):
        try:
            top_type = request.query_params.get("top")
            guard(top_type, "top parameter is required")
            guard(validate_top_type(top_type), 'top must be "user", "country", or "blog"')

            filter_dict, date_range = get_filters_and_range(request, allow_range=True)

            queryset = BlogView.objects.all()

            if date_range:
                start, end = date_range
                queryset = queryset.filter(viewed_at__gte=start, viewed_at__lte=end)

            if filter_dict:
                queryset = apply_filters(queryset, filter_dict)

            # Perform top-type grouping
            if top_type == "user":
                results = queryset.values(
                    "viewer__username", "viewer__country__name"
                ).annotate(
                    total_views=Count("id")
                ).filter(
                    viewer__username__isnull=False
                ).order_by("-total_views")[:10]

                data = [
                    {
                        "x": r["viewer__username"],
                        "y": r["viewer__country__name"] or "Unknown",
                        "z": r["total_views"],
                    }
                    for r in results
                ]

            elif top_type == "country":
                results = queryset.values("country__name").annotate(
                    blog_count=Count("blog", distinct=True),
                    total_views=Count("id"),
                ).filter(
                    country__name__isnull=False
                ).order_by("-total_views")[:10]

                data = [
                    {"x": r["country__name"], "y": r["blog_count"], "z": r["total_views"]}
                    for r in results
                ]

            else:  # blog
                results = queryset.values(
                    "blog__title", "blog__author__username"
                ).annotate(
                    total_views=Count("id")
                ).order_by("-total_views")[:10]

                data = [
                    {
                        "x": r["blog__title"],
                        "y": r["blog__author__username"],
                        "z": r["total_views"],
                    }
                    for r in results
                ]

            return Response(TopSerializer(data, many=True).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PerformanceAPIView(APIView):

    @extend_schema(
        summary="Performance Time Series",
        parameters=[
            OpenApiParameter(
                name="compare",
                required=True,
                enum=['month', 'week', 'day', 'year']
            ),
            OpenApiParameter(
                name="user_id",
                required=False,
                type=OpenApiTypes.INT
            ),
            OpenApiParameter(
                name="filters",
                required=False
            ),
        ],
        responses={200: PerformanceSerializer(many=True)},
        tags=["Analytics"],
    )
    def get(self, request):
        try:
            compare_type = request.query_params.get("compare")
            guard(compare_type, "compare is required")
            guard(validate_compare(compare_type), "Invalid compare type")

            user_id = request.query_params.get("user_id")

            filter_dict, _ = get_filters_and_range(request, allow_range=False)

            trunc_func = get_trunc_function(compare_type)

            # Build views queryset
            views_qs = BlogView.objects.all()

            if user_id:
                views_qs = views_qs.filter(blog__author_id=user_id)

            if filter_dict:
                views_qs = apply_filters(views_qs, filter_dict)

            # Views aggregated by period
            period_views = views_qs.annotate(
                period=trunc_func("viewed_at")
            ).values("period").annotate(
                total_views=Count("id")
            ).order_by("period")

            # Blog creations aggregated by period
            blogs_qs = Blog.objects.all()
            if user_id:
                blogs_qs = blogs_qs.filter(author_id=user_id)

            period_blogs = blogs_qs.annotate(
                period=trunc_func("created_at")
            ).values("period").annotate(
                blog_count=Count("id")
            ).order_by("period")

            views_dict = {i["period"]: i["total_views"] for i in period_views}
            blogs_dict = {i["period"]: i["blog_count"] for i in period_blogs}

            all_periods = sorted(set(views_dict.keys()) | set(blogs_dict.keys()))

            data = []
            previous_views = 0

            for period in all_periods:
                current = views_dict.get(period, 0)
                blogs = blogs_dict.get(period, 0)

                growth = calculate_growth_percentage(current, previous_views)
                label = format_period_label(period, compare_type, blogs)

                data.append({"x": label, "y": current, "z": growth})
                previous_views = current

            return Response(PerformanceSerializer(data, many=True).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        except Exception as e:
            return Response({"error": f"Server error: {str(e)}"}, status=500)
