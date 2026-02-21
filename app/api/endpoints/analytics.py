from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api import deps
from app.db.session import get_db
from app.models.admin import User, Style, Category, Admin

router = APIRouter()

@router.get("/stats", response_model=dict)
def get_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    Get overview stats for the dashboard.
    """
    total_users = db.query(User).count()
    new_users_today = db.query(User).filter(User.created_at >= datetime.now().date()).count()
    total_styles = db.query(Style).count()
    total_categories = db.query(Category).count()
    
    # Mock data for other fields
    return {
        "success": True,
        "data": {
            "users": {
                "total": total_users,
                "new_today": new_users_today,
                "growth": 12.5
            },
            "creations": {
                "total": 1250,
                "today": 45,
                "growth": 8.2
            },
            "revenue": {
                "total": 4500,
                "this_month": 1200,
                "growth": 15.3
            },
            "activity": {
                "active_users": 156,
                "avg_session": "12m 30s"
            }
        }
    }

@router.get("/activity", response_model=dict)
def get_activity(
    db: Session = Depends(get_db),
    admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    Get recent system activity.
    """
    # Mock activity data
    return {
        "success": True,
        "data": {
            "activities": [
                {
                    "id": 1,
                    "type": "user_signup",
                    "user": "John Doe",
                    "description": "New user registered",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "type": "creation",
                    "user": "Alice Smith",
                    "description": "Generated a new image with Neon style",
                    "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()
                }
            ]
        }
    }

@router.get("/charts", response_model=dict)
def get_charts(
    metric: str = Query("users"),
    range: str = Query("7d"),
    db: Session = Depends(get_db),
    admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    Get data for dashboard charts.
    """
    # Mock chart data
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if metric == "users":
        data = [12, 19, 3, 5, 2, 3, 7]
    elif metric == "creations":
        data = [45, 52, 38, 65, 48, 23, 30]
    else:
        data = [100, 200, 150, 300, 250, 400, 350]
        
    return {
        "success": True,
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": metric.capitalize(),
                    "data": data
                }
            ]
        }
    }
