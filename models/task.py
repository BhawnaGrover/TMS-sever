from db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from datetime import datetime
import enum


class StatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    overdue = "overdue"

class PriorityEnum(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

#task model
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(SQLAlchemyEnum(PriorityEnum), default=PriorityEnum.low)
    due_date = Column(DateTime)
    status = Column(SQLAlchemyEnum(StatusEnum), default=StatusEnum.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=None, onupdate=datetime.utcnow)

