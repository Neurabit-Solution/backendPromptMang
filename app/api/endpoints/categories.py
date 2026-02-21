from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import re

from app.api import deps
from app.db.session import SessionLocal
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

@router.get("/", response_model=List[schemas.CategoryResponse])
@router.get("", response_model=List[schemas.CategoryResponse])
def get_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve categories.
    """
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

@router.post("/", response_model=schemas.CategoryResponse)
@router.post("", response_model=schemas.CategoryResponse)
async def create_category(
    *,
    db: Session = Depends(deps.get_db),
    name: str = Form(...),
    icon: str = Form(...),
    description: str = Form(...),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    preview_image: Optional[UploadFile] = File(None),
) -> Any:
    """
    Create new category.
    """
    slug = generate_slug(name)
    
    # Check if category already exists
    existing = db.query(models.Category).filter(models.Category.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A category with this name/slug already exists.",
        )
    
    preview_url = None
    if preview_image:
        extension = preview_image.filename.split('.')[-1]
        object_name = f"categories/thumbnails/{slug}.{extension}"
        content = await preview_image.read()
        preview_url = s3_service.upload_file(content, object_name, preview_image.content_type)
        
        if not preview_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload category preview image to S3.",
            )

    db_obj = models.Category(
        name=name,
        slug=slug,
        icon=icon,
        description=description,
        display_order=display_order,
        is_active=is_active,
        preview_url=preview_url
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{id}", response_model=schemas.CategoryResponse)
async def update_category(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    name: Optional[str] = Form(None),
    icon: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    display_order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    preview_image: Optional[UploadFile] = File(None),
) -> Any:
    """
    Update a category.
    """
    db_obj = db.query(models.Category).filter(models.Category.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if name:
        db_obj.name = name
        db_obj.slug = generate_slug(name)
    if icon:
        db_obj.icon = icon
    if description:
        db_obj.description = description
    if display_order is not None:
        db_obj.display_order = display_order
    if is_active is not None:
        db_obj.is_active = is_active
        
    if preview_image:
        extension = preview_image.filename.split('.')[-1]
        object_name = f"categories/thumbnails/{db_obj.slug}.{extension}"
        content = await preview_image.read()
        preview_url = s3_service.upload_file(content, object_name, preview_image.content_type)
        
        if not preview_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload category preview image to S3.",
            )
        db_obj.preview_url = preview_url

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/{id}")
def delete_category(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Delete a category.
    """
    db_obj = db.query(models.Category).filter(models.Category.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has styles
    if db_obj.styles:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category because it has associated styles. Delete or reassign styles first."
        )
        
    db.delete(db_obj)
    db.commit()
    return {"success": True, "message": "Category deleted successfully"}
