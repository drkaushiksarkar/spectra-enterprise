"""Vector type definitions."""
from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime


class VectorRecord(TypedDict):
    id: str
    name: str
    type: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: Optional[str]


class VectorQuery(TypedDict, total=False):
    limit: int
    offset: int
    filter: str
    sort_by: str
    order: str


class VectorResponse(TypedDict):
    data: List[VectorRecord]
    total: int
    page: int
    has_more: bool
