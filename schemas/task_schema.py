from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class StatusEnum(str, Enum):
    pending = "pending"
    completed = "completed"
    overdue = "overdue"
    
class PriorityEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    due_date: str
    priority: PriorityEnum

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None

class TaskResponse(TaskBase):
    id: int
    status: StatusEnum
    priority: PriorityEnum
    due_date: Optional[datetime] = None

class TaskIndResponse(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    status: Optional[StatusEnum] = None
    created_at: Optional[datetime] = None
    update_at: Optional[datetime] = None

class SearchTask(BaseModel):
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    status: Optional[StatusEnum] = None

class Config:
    orm_mode = True