from fastapi import Query

from netwiz_backend.models import PaginationParams


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
) -> PaginationParams:
    """Dependency to get pagination parameters"""
    return PaginationParams(page=page, page_size=page_size)
