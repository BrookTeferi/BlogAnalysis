"""
Utility functions for analytics calculations and date handling.
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay, TruncYear
from typing import Tuple, Optional


def get_date_range(range_type: str) -> Tuple[datetime, datetime]:
    """
    Get start and end dates for a given range type.
    
    Args:
        range_type: 'month', 'week', or 'year'
        
    Returns:
        Tuple of (start_date, end_date)
    """
    now = timezone.now()
    
    if range_type == 'month':
        # Last 30 days
        start_date = now - timedelta(days=30)
    elif range_type == 'week':
        # Last 7 days
        start_date = now - timedelta(days=7)
    elif range_type == 'year':
        # Last 365 days
        start_date = now - timedelta(days=365)
    else:
        raise ValueError(f"Invalid range type: {range_type}. Must be 'month', 'week', or 'year'")
    
    return start_date, now


def get_trunc_function(compare_type: str):
    """
    Get the appropriate Django Trunc function for time-series grouping.
    
    Args:
        compare_type: 'month', 'week', 'day', or 'year'
        
    Returns:
        Django Trunc function class
    """
    trunc_map = {
        'month': TruncMonth,
        'week': TruncWeek,
        'day': TruncDay,
        'year': TruncYear,
    }
    
    if compare_type not in trunc_map:
        raise ValueError(
            f"Invalid compare type: {compare_type}. "
            f"Must be one of: {', '.join(trunc_map.keys())}"
        )
    
    return trunc_map[compare_type]


def calculate_growth_percentage(current: float, previous: float) -> str:
    """
    Calculate growth/decline percentage between two values.
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        Formatted percentage string (e.g., "+12.5%" or "-8.3%")
    """
    if previous == 0:
        if current == 0:
            return "0.0%"
        else:
            return "+100.0%"  # Infinite growth, cap at 100%
    
    percentage = ((current - previous) / previous) * 100
    
    # Format with sign
    if percentage >= 0:
        return f"+{percentage:.1f}%"
    else:
        return f"{percentage:.1f}%"


def format_period_label(date: datetime, compare_type: str, blog_count: int) -> str:
    """
    Format a period label for performance API.
    
    Args:
        date: Date to format
        compare_type: 'month', 'week', 'day', or 'year'
        blog_count: Number of blogs created in this period
        
    Returns:
        Formatted label (e.g., "2024-01 (15 blogs)")
    """
    if compare_type == 'month':
        period = date.strftime('%Y-%m')
    elif compare_type == 'week':
        period = date.strftime('%Y-W%U')  # Year-Week number
    elif compare_type == 'day':
        period = date.strftime('%Y-%m-%d')
    elif compare_type == 'year':
        period = date.strftime('%Y')
    else:
        period = str(date)
    
    blog_text = "blog" if blog_count == 1 else "blogs"
    return f"{period} ({blog_count} {blog_text})"


def validate_range(range_type: Optional[str]) -> bool:
    """
    Validate range type parameter.
    
    Args:
        range_type: Range type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return range_type in ['month', 'week', 'year']


def validate_compare(compare_type: Optional[str]) -> bool:
    """
    Validate compare type parameter.
    
    Args:
        compare_type: Compare type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return compare_type in ['month', 'week', 'day', 'year']


def validate_object_type(object_type: Optional[str]) -> bool:
    """
    Validate object type parameter.
    
    Args:
        object_type: Object type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return object_type in ['country', 'user']


def validate_top_type(top_type: Optional[str]) -> bool:
    """
    Validate top type parameter.
    
    Args:
        top_type: Top type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return top_type in ['user', 'country', 'blog']
