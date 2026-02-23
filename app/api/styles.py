"""
Styles & Categories API
-----------------------
GET  /api/styles            → list all active styles (with optional filters)
GET  /api/styles/trending   → top trending styles for the "Hot Right Now" section
GET  /api/categories        → list all active categories
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.database import get_db
from app.models.style import Style, Category
from app.schemas.style import StyleOut, StyleListResponse, CategoryOut

router = APIRouter(prefix="/styles", tags=["Styles"])
categories_router = APIRouter(prefix="/categories", tags=["Categories"])


# ─── Helper ───────────────────────────────────────────────────────────────────


from app.core.s3 import get_proxy_url

def _style_to_out(style: Style) -> StyleOut:
    return StyleOut(
        id=style.id,
        name=style.name,
        slug=style.slug or f"style-{style.id}",  # fallback if DB has NULL slug
        description=style.description,
        preview_url=get_proxy_url(style.preview_url),
        category=CategoryOut(
            id=style.category.id,
            name=style.category.name,
            slug=style.category.slug or f"category-{style.category.id}",
            icon=style.category.icon,
            description=style.category.description,
            preview_url=get_proxy_url(style.category.preview_url),
            display_order=style.category.display_order,
        ),
        uses_count=style.uses_count,
        is_trending=style.is_trending,
        is_new=style.is_new,
        tags=style.tags or [],
        credits_required=style.credits_required,
    )


# ─── Styles Endpoints ─────────────────────────────────────────────────────────

@router.get("", response_model=StyleListResponse)
def list_styles(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    category_id: Optional[int] = Query(None, description="Filter by category id"),
    trending: Optional[bool] = Query(None, description="Only trending styles"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: Session = Depends(get_db),
):
    """
    Returns all active styles.
    Used by the frontend to render the home screen style grid.
    Each style includes its S3 thumbnail URL and the category it belongs to.
    Filter by category using either category (slug) or category_id; category_id takes precedence if both are set.
    """
    query = (
        db.query(Style)
        .options(joinedload(Style.category))
        .filter(Style.is_active == True)
    )

    if category_id is not None:
        query = query.filter(Style.category_id == category_id)
    elif category:
        query = query.join(Category).filter(Category.slug == category)

    if trending is True:
        query = query.filter(Style.is_trending == True)

    if search:
        query = query.filter(Style.name.ilike(f"%{search}%"))

    query = query.order_by(Style.display_order.asc(), Style.uses_count.desc())

    styles = query.all()
    return StyleListResponse(
        success=True,
        data=[_style_to_out(s) for s in styles],
        total=len(styles),
    )


@router.get("/trending", response_model=StyleListResponse)
def trending_styles(db: Session = Depends(get_db)):
    """
    Returns the top trending styles for the 'Hot Right Now' section on the home screen.
    Limited to 10 results, sorted by usage count.
    """
    styles = (
        db.query(Style)
        .options(joinedload(Style.category))
        .filter(Style.is_active == True, Style.is_trending == True)
        .order_by(Style.uses_count.desc())
        .limit(10)
        .all()
    )
    return StyleListResponse(
        success=True,
        data=[_style_to_out(s) for s in styles],
        total=len(styles),
    )


# ─── Categories Endpoint ──────────────────────────────────────────────────────

@categories_router.get("")
def list_categories(db: Session = Depends(get_db)):
    """
    Returns all active categories.
    Used by the frontend to render the category filter tabs.
    """
    categories = (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.display_order.asc())
        .all()
    )

    data = []
    for cat in categories:
        styles_count = db.query(Style).filter(
            Style.category_id == cat.id,
            Style.is_active == True
        ).count()


        data.append(CategoryOut(
            id=cat.id,
            name=cat.name,
            slug=cat.slug or f"category-{cat.id}",
            icon=cat.icon,
            description=cat.description,
            preview_url=get_proxy_url(cat.preview_url),
            display_order=cat.display_order,
            styles_count=styles_count,
        ))

    return {"success": True, "data": data}
