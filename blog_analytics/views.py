from django.db.models import Count, F, Value
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from datetime import timedelta
import json


from .models import Blog
from .serializers import BlogViewsSerializer, TopSerializer, PerformanceSerializer
from .filters import apply_filters
from .utils import calculate_growth_percentage, format_period_label


def safe_json_loads(value):
    """Safely parse JSON string or return None. Raises ValueError on invalid JSON."""
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in 'filters' parameter: {e}")


def get_date_range(request):
    start_str = request.query_params.get("start_date")
    end_str = request.query_params.get("end_date")
    range_type = request.query_params.get("range")

    if start_str and end_str:
        from datetime import datetime
        try:
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            if start > end:
                raise ValueError("start_date cannot be after end_date")
            return start.replace(tzinfo=timezone.utc), end.replace(tzinfo=timezone.utc)
        except Exception:
            raise ValueError("Invalid date format. Use ISO 8601 (e.g. 2025-12-01)")

    now = timezone.now()
    days = {"week": 7, "month": 30, "year": 365}.get(range_type, 30)
    return now - timedelta(days=days), now


class BlogViewsAPIView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name="object_type", required=True, enum=["country", "user"]),
            OpenApiParameter(name="range", required=False, enum=["week", "month", "year"]),
            OpenApiParameter(name="start_date", type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name="end_date", type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name="filters", type=OpenApiTypes.STR, required=False, description="JSON string"),
        ],
        responses=BlogViewsSerializer(many=True)
    )
    def get(self, request):
        object_type = request.query_params.get("object_type")
        if object_type not in ["country", "user"]:
            return Response({"error": "object_type must be 'country' or 'user'"}, status=400)

        try:
            start_date, end_date = get_date_range(request)
            filter_dict = safe_json_loads(request.query_params.get("filters"))

            qs = Blog.objects.filter(
                views__viewed_at__gte=start_date,
                views__viewed_at__lte=end_date
            )

            if filter_dict:
                qs = apply_filters(qs, filter_dict)

            if object_type == "country":
                results = qs.values(country_name=F("author__country__name")) \
                    .annotate(
                        num_blogs=Count("id", distinct=True),
                        total_views=Count("views")
                    ).order_by("-total_views")

                data = [
                    {"x": r["country_name"] or "Unknown", "y": r["num_blogs"], "z": r["total_views"]}
                    for r in results
                ]
            else:  # user
                results = qs.values(username=F("author__username")) \
                    .annotate(
                        num_blogs=Count("id", distinct=True),
                        total_views=Count("views")
                    ).order_by("-total_views")

                data = [
                    {"x": r["username"] or "Anonymous", "y": r["num_blogs"], "z": r["total_views"]}
                    for r in results
                ]

            return Response(BlogViewsSerializer(data, many=True).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)

class TopAPIView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name="top", required=True, enum=["user", "country", "blog"]),
            OpenApiParameter(name="range", required=False),
            OpenApiParameter(name="start_date", required=False),
            OpenApiParameter(name="end_date", required=False),
            OpenApiParameter(name="filters", required=False),
        ],
        responses=TopSerializer(many=True)
    )
    def get(self, request):
        top_type = request.query_params.get("top")
        if top_type not in ["user", "country", "blog"]:
            return Response({"error": "top must be user/country/blog"}, status=400)

        try:
            start_date, end_date = get_date_range(request)
            filter_dict = safe_json_loads(request.query_params.get("filters"))

            base_qs = Blog.objects.filter(
                views__viewed_at__gte=start_date,
                views__viewed_at__lte=end_date
            )

            if filter_dict:
                base_qs = apply_filters(base_qs, filter_dict)

            if top_type == "country":
                results = base_qs.values("author__country__name") \
                    .annotate(blogs=Count("id", distinct=True), views=Count("views")) \
                    .order_by("-views")[:10]
                data = [
                    {"x": r["author__country__name"] or "Unknown", "y": r["blogs"], "z": r["views"]}
                    for r in results
                ]

            elif top_type == "user":
                results = base_qs.values("author__username") \
                    .annotate(blogs=Count("id", distinct=True), views=Count("views")) \
                    .order_by("-views")[:10]
                data = [
                    {"x": r["author__username"] or "Anonymous", "y": r["blogs"], "z": r["views"]}
                    for r in results
                ]

            else: 
                results = base_qs.values("title") \
                    .annotate(
                        author_name=F("author__username"), 
                        views=Count("views")
                    ) \
                    .order_by("-views")[:10]

                data = [
                    {"x": r["title"], "y": r["author_name"] or "Anonymous", "z": r["views"]}
                    for r in results
                ]

            return Response(TopSerializer(data, many=True).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)

class PerformanceAPIView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name="compare", required=True, enum=["day", "week", "month", "year"]),
            OpenApiParameter(name="user_id", required=False),
            OpenApiParameter(name="filters", required=False),
        ],
        responses=PerformanceSerializer(many=True)
    )
    def get(self, request):
        compare = request.query_params.get("compare")
        if compare not in ["day", "week", "month", "year"]:
            return Response({"error": "compare must be day/week/month/year"}, status=400)

        try:
            user_id = request.query_params.get("user_id")
            filter_dict = safe_json_loads(request.query_params.get("filters"))

            Trunc = {"day": TruncDay, "week": TruncWeek, "month": TruncMonth, "year": TruncYear}[compare]

            qs = Blog.objects.all()
            if user_id:
                qs = qs.filter(author_id=user_id)
            if filter_dict:
                qs = apply_filters(qs, filter_dict)

            current = qs.annotate(period=Trunc("views__viewed_at")) \
                .values("period") \
                .annotate(
                    views=Count("views"),
                    blogs_created=Count("id", distinct=True)
                ).order_by("period")

            shift_days = {"day": 1, "week": 7, "month": 30, "year": 365}[compare]
            previous = qs.annotate(
                period=Trunc(F("views__viewed_at") - Value(timedelta(days=shift_days)))
            ).values("period").annotate(views=Count("views"))
            prev_dict = {item["period"]: item["views"] for item in previous}

            data = []
            for item in current:
                prev = prev_dict.get(item["period"], 0)
                if prev == 0:
                    growth = "N/A" if item["views"] == 0 else "+∞%"
                else:
                    growth = calculate_growth_percentage(item["views"], prev)
                label = format_period_label(item["period"], compare, item["blogs_created"])
                data.append({"x": label, "y": item["views"], "z": growth})

            return Response(PerformanceSerializer(data, many=True).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception:
            return Response({"error": "Internal server error"}, status=500)