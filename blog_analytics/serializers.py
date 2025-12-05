from rest_framework import serializers


class BlogViewsSerializer(serializers.Serializer):
    """Serializer for blog-views endpoint response."""
    x = serializers.CharField(help_text="Grouping key (country name or username)")
    y = serializers.IntegerField(help_text="Number of blogs")
    z = serializers.IntegerField(help_text="Total views")


class TopSerializer(serializers.Serializer):
    """Serializer for top endpoint response."""
    x = serializers.CharField(help_text="Primary identifier")
    y = serializers.CharField(help_text="Secondary information")
    z = serializers.IntegerField(help_text="Total views")


class PerformanceSerializer(serializers.Serializer):
    """Serializer for performance endpoint response."""
    x = serializers.CharField(help_text="Period label with blog count")
    y = serializers.IntegerField(help_text="Views during period")
    z = serializers.CharField(help_text="Growth/decline percentage")
