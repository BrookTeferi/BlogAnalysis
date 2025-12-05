from django.db.models import Q
from typing import Dict, Any, List


class DynamicFilter:
    SUPPORTED_OPERATIONS = ['and', 'or', 'not', 'eq', 'in', 'contains', 'gt', 'gte', 'lt', 'lte']

    def __init__(self, filter_dict: Dict[str, Any]):
        self.filter_dict = filter_dict or {}

    def parse(self) -> Q:
        if not self.filter_dict:
            return Q()
        return self._parse_node(self.filter_dict)

    def _parse_node(self, node: Any) -> Q:
        if not isinstance(node, dict):
            raise ValueError(f"Filter node must be a dict, got {type(node)}")

        if "field" in node and "op" in node:
            return self._build_condition(node)

        operations = [k for k in node.keys() if k in self.SUPPORTED_OPERATIONS]
        if not operations:
            raise ValueError(f"No valid operation in node: {node.keys()}")
        if len(operations) > 1:
            raise ValueError("Only one operation per node allowed")

        op = operations[0]
        value = node[op]

        if op == "and":
            return self._parse_and(value)
        elif op == "or":
            return self._parse_or(value)
        elif op == "not":
            return ~self._parse_node(value)
        else:
            raise ValueError(f"Unsupported operation: {op}")

    def _build_condition(self, cond: dict) -> Q:
        field = cond["field"]
        op = cond.get("op", "eq")
        value = cond["value"]

        lookup_map = {
            "eq": "",
            "in": "__in",
            "contains": "__icontains",
            "gt": "__gt",
            "gte": "__gte",
            "lt": "__lt",
            "lte": "__lte",
        }

        if op not in lookup_map:
            raise ValueError(f"Unsupported operator: {op}")

        lookup = f"{field}{lookup_map[op]}"
        return Q(**{lookup: value})

    def _parse_and(self, conditions: List) -> Q:
        if not isinstance(conditions, list):
            raise ValueError("AND requires a list")
        q = Q()
        for cond in conditions:
            q &= self._parse_node(cond)
        return q

    def _parse_or(self, conditions: List) -> Q:
        if not isinstance(conditions, list):
            raise ValueError("OR requires a list")
        q = Q()
        for cond in conditions:
            q |= self._parse_node(cond)
        return q


def apply_filters(queryset, filter_dict: Dict[str, Any]):
    if not filter_dict:
        return queryset
    try:
        parser = DynamicFilter(filter_dict)
        return queryset.filter(parser.parse()).distinct()
    except Exception as e:
        raise ValueError(f"Invalid filter syntax: {e}")