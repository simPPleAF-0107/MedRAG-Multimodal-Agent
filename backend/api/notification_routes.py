from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any

from backend.database.db import get_db
from backend.database.models import User, Notification
from backend.database import schemas
from backend.api.deps import get_current_active_user

router = APIRouter(tags=["Notifications"])

@router.get("/notifications", response_model=List[schemas.NotificationResponse])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Fetch unread notifications for the currently logged-in user.
    """
    query = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/notifications/{notification_id}/read", response_model=schemas.NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Manually mark a notification as read.
    """
    query = select(Notification).where(Notification.id == notification_id)
    result = await db.execute(query)
    notification = result.scalars().first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification
