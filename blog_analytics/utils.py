from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay, TruncYear
from typing import Tuple, Optional


def get_date_range(range_type: str) -> Tuple[datetime, datetime]:
    now = timezone.now()
    
    if range_type == 'month':

        start_date = now - timedelta(days=30)
    elif range_type == 'week':
        
        start_date = now - timedelta(days=7)
    elif range_type == 'year':

        start_date = now - timedelta(days=365)
    else:
        raise ValueError(f"Invalid range type: {range_type}. Must be 'month', 'week', or 'year'")
    
    return start_date, now


def get_trunc_function(compare_type: str):
    
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
    
    if previous == 0:
        if current == 0:
            return "0.0%"
        else:
            return "+100.0%"  
    
    percentage = ((current - previous) / previous) * 100

    if percentage >= 0:
        return f"+{percentage:.1f}%"
    else:
        return f"{percentage:.1f}%"


def format_period_label(date: datetime, compare_type: str, blog_count: int) -> str:
    if compare_type == 'month':
        period = date.strftime('%Y-%m')
    elif compare_type == 'week':
        period = date.strftime('%Y-W%U') 
    elif compare_type == 'day':
        period = date.strftime('%Y-%m-%d')
    elif compare_type == 'year':
        period = date.strftime('%Y')
    else:
        period = str(date)
    
    blog_text = "blog" if blog_count == 1 else "blogs"
    return f"{period} ({blog_count} {blog_text})"


def validate_range(range_type: Optional[str]) -> bool:
    return range_type in ['month', 'week', 'year']


def validate_compare(compare_type: Optional[str]) -> bool:
     return compare_type in ['month', 'week', 'day', 'year']


def validate_object_type(object_type: Optional[str]) -> bool:
    return object_type in ['country', 'user']


def validate_top_type(top_type: Optional[str]) -> bool:
    return top_type in ['user', 'country', 'blog']
