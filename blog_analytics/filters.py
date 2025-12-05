
from django.db.models import Q
from typing import Dict, Any, List


class DynamicFilter:
    
    
    SUPPORTED_OPERATIONS = ['and', 'or', 'not', 'eq']
    
    def __init__(self, filter_dict: Dict[str, Any]):
        """
        Initialize the filter parser.
        
        Args:
            filter_dict: Dictionary containing filter operations
        """
        self.filter_dict = filter_dict or {}
    
    def parse(self) -> Q:
        """
        Parse the filter dictionary and return a Django Q object.
        
        Returns:
            Q object representing the filter conditions
        """
        if not self.filter_dict:
            return Q()
        
        return self._parse_node(self.filter_dict)
    
    def _parse_node(self, node: Dict[str, Any]) -> Q:
        """
        Recursively parse a filter node.
        
        Args:
            node: Dictionary node to parse
            
        Returns:
            Q object for this node
        """
        if not isinstance(node, dict):
            raise ValueError(f"Filter node must be a dictionary, got {type(node)}")
        
        # Get the operation (should be only one key at top level)
        operations = [k for k in node.keys() if k in self.SUPPORTED_OPERATIONS]
        
        if not operations:
            raise ValueError(f"No valid operation found in node: {node}")
        
        if len(operations) > 1:
            raise ValueError(f"Multiple operations in single node: {operations}")
        
        operation = operations[0]
        value = node[operation]
        
        if operation == 'and':
            return self._parse_and(value)
        elif operation == 'or':
            return self._parse_or(value)
        elif operation == 'not':
            return self._parse_not(value)
        elif operation == 'eq':
            return self._parse_eq(value)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    def _parse_and(self, conditions: List[Dict[str, Any]]) -> Q:
        """Parse AND operation."""
        if not isinstance(conditions, list):
            raise ValueError("AND operation requires a list of conditions")
        
        if not conditions:
            return Q()
        
        q = Q()
        for condition in conditions:
            q &= self._parse_node(condition)
        
        return q
    
    def _parse_or(self, conditions: List[Dict[str, Any]]) -> Q:
        """Parse OR operation."""
        if not isinstance(conditions, list):
            raise ValueError("OR operation requires a list of conditions")
        
        if not conditions:
            return Q()
        
        q = Q()
        for condition in conditions:
            q |= self._parse_node(condition)
        
        return q
    
    def _parse_not(self, condition: Dict[str, Any]) -> Q:
        """Parse NOT operation."""
        if not isinstance(condition, dict):
            raise ValueError("NOT operation requires a dictionary condition")
        
        return ~self._parse_node(condition)
    
    def _parse_eq(self, fields: Dict[str, Any]) -> Q:
        """
        Parse EQ (equality) operation.
        
        Supports Django field lookups like:
        - field__exact
        - field__icontains
        - field__gt, field__lt, etc.
        - Related field lookups: country__code, blog__author__username
        """
        if not isinstance(fields, dict):
            raise ValueError("EQ operation requires a dictionary of field-value pairs")
        
        q = Q()
        for field, value in fields.items():
            q &= Q(**{field: value})
        
        return q


def apply_filters(queryset, filter_dict: Dict[str, Any]):
    """
    Apply dynamic filters to a QuerySet.
    
    Args:
        queryset: Django QuerySet to filter
        filter_dict: Dictionary containing filter operations
        
    Returns:
        Filtered QuerySet
    """
    if not filter_dict:
        return queryset
    
    try:
        dynamic_filter = DynamicFilter(filter_dict)
        q_object = dynamic_filter.parse()
        return queryset.filter(q_object)
    except Exception as e:
        raise ValueError(f"Invalid filter: {str(e)}")


def validate_filters(filter_dict: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate filter dictionary without applying it.
    
    Args:
        filter_dict: Dictionary containing filter operations
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filter_dict:
        return True, ""
    
    try:
        dynamic_filter = DynamicFilter(filter_dict)
        dynamic_filter.parse()
        return True, ""
    except Exception as e:
        return False, str(e)
