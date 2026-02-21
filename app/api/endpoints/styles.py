from typing import Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import json
import re

from app.api import deps
from app.db.session import get_db
from app.models import admin as models
from app.schemas import admin as schemas
from app.core.s3 import s3_service

router = APIRouter()

def generate_slug(name: str) -> str:
    # Convert to lowercase, replace spaces with hyphens, remove special characters
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug

@router.get("/", response_model=List[schemas.StyleResponse])
@router.get("", response_model=List[schemas.StyleResponse])
def get_styles(
    db: Session = Depends(deps.get_db),
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve styles.
    """
    query = db.query(models.Style)
    if category_id:
        query = query.filter(models.Style.category_id == category_id)
    styles = query.offset(skip).limit(limit).all()
    return styles

@router.get("/{id}", response_model=schemas.StyleResponse)
@router.get("/{id}/", response_model=schemas.StyleResponse)
def get_style(
    *,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(deps.get_current_admin),
    id: int,
) -> Any:
    """
    Get style by ID.
    """
    style = db.query(models.Style).filter(models.Style.id == id).first()
    if not style:
        raise HTTPException(status_code=404, detail="Style not found")
    return style

@router.post("/", response_model=schemas.StyleResponse)
@router.post("", response_model=schemas.StyleResponse)
async def create_style(
    *,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(deps.require_permission("styles.manage")),
    category_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    prompt_template: str = Form(...),
    negative_prompt: Optional[str] = Form(None),
    tags: str = Form('[]'),  # JSON string
    credits_required: int = Form(50),
    display_order: int = Form(0),
    is_trending: bool = Form(False),
    is_new: bool = Form(True),
    is_active: bool = Form(True),
    preview_image: UploadFile = File(...),
) -> Any:
    """
    Create new style.
    """
    # Check if category exists
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    slug = generate_slug(name)
    
    # Upload image to S3
    extension = preview_image.filename.split('.')[-1]
    object_name = f"styles/thumbnails/{slug}.{extension}"
    content = await preview_image.read()
    preview_url = s3_service.upload_file(content, object_name, preview_image.content_type)
    
    if not preview_url:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload style preview image to S3.",
        )

    try:
        tags_list = json.loads(tags)
    except:
        tags_list = []

    import time
    db_obj = models.Style(
        category_id=category_id,
        name=name,
        description=description,
        prompt_template=prompt_template,
        negative_prompt=negative_prompt,
        tags=tags_list,
        credits_required=credits_required,
        display_order=display_order,
        is_trending=is_trending,
        is_new=is_new,
        is_active=is_active,
        preview_url=f"{preview_url}?v={int(time.time())}"
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{id}", response_model=schemas.StyleResponse)
@router.put("/{id}/", response_model=schemas.StyleResponse)
async def update_style(
    *,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(deps.require_permission("styles.manage")),
    id: int,
    category_id: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    prompt_template: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    credits_required: Optional[int] = Form(None),
    display_order: Optional[int] = Form(None),
    is_trending: Optional[bool] = Form(None),
    is_new: Optional[bool] = Form(None),
    is_active: Optional[bool] = Form(None),
    preview_image: Optional[UploadFile] = File(None),
) -> Any:
    """
    Update a style.
    """
    db_obj = db.query(models.Style).filter(models.Style.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Style not found")
    
    if category_id:
        category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_obj.category_id = category_id
        
    if name:
        db_obj.name = name
    if description:
        db_obj.description = description
    if prompt_template:
        db_obj.prompt_template = prompt_template
    if negative_prompt is not None:
        db_obj.negative_prompt = negative_prompt
    if tags:
        try:
            db_obj.tags = json.loads(tags)
        except:
            pass
    if credits_required is not None:
        db_obj.credits_required = credits_required
    if display_order is not None:
        db_obj.display_order = display_order
    if is_trending is not None:
        db_obj.is_trending = is_trending
    if is_new is not None:
        db_obj.is_new = is_new
    if is_active is not None:
        db_obj.is_active = is_active
        
    if preview_image:
        slug = generate_slug(db_obj.name)
        extension = preview_image.filename.split('.')[-1]
        object_name = f"styles/thumbnails/{slug}.{extension}"
        content = await preview_image.read()
        preview_url = s3_service.upload_file(content, object_name, preview_image.content_type)
        
        if not preview_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload style preview image to S3.",
            )
        
        import time
        preview_url = f"{preview_url}?v={int(time.time())}"
        db_obj.preview_url = preview_url

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/{id}")
@router.delete("/{id}/")
def delete_style(
    *,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(deps.require_permission("styles.manage")),
    id: int,
) -> Any:
    """
    Delete a style.
    """
    db_obj = db.query(models.Style).filter(models.Style.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Style not found")
        
    db.delete(db_obj)
    db.commit()
    return {"success": True, "message": "Style deleted successfully"}
