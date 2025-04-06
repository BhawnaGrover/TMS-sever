from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from schemas.task_schema import TaskResponse, TaskUpdate, TaskCreate, TaskIndResponse, SearchTask
from sqlalchemy.orm import Session
from db.session import get_db 
from models.user import User
from models.task import Task
from datetime import datetime, timedelta
from .user_router import get_current_user
from typing import Optional
from enum import Enum

class StatusEnum(str, Enum):
    pending = "pending"
    completed = "completed" 
    overdue = "overdue"
    
class PriorityEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
# Load the model and tokenizer from the local directory
task_router_tms = APIRouter()

# Get all tasks
@task_router_tms.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    today = datetime.today().date()
    update_count = 0
    for task in tasks:
        # print(f"Task: {task.id}, Status: {task.status}, Due date: {task.due_date}")
        if task.status != StatusEnum.pending and task.due_date:
            task_due_date = task.due_date.date() if isinstance(task.due_date, datetime) else task.due_date
            if task_due_date < today:
                task.status = StatusEnum.overdue
                db.add(task)
                update_count += 1

    db.commit()
    # db.refresh(tasks)
    return tasks

# Get task by ID
@task_router_tms.get("/task/{task_id}", response_model=TaskIndResponse)
def get_task_by_id(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

#create task
@task_router_tms.post("/task", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task_dict = task.dict()
    task_dict['user_id'] = current_user.id
    
    # Parse the date from DD-MM-YYYY format to a datetime object
    if task_dict['due_date']:
        try:
            # Try ISO format first (YYYY-MM-DD)
            task_dict['due_date'] = datetime.fromisoformat(task_dict['due_date'])
        except ValueError:
            # If that fails, try DD-MM-YYYY format
            day, month, year = map(int, task_dict['due_date'].split('-'))
            task_dict['due_date'] = datetime(year, month, day)
    
    task_to_be_created = Task(**task_dict)
    db.add(task_to_be_created)
    db.commit()
    db.refresh(task_to_be_created)
    return task_to_be_created

#update task
@task_router_tms.put("/task/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = task.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item
    
# Delete task
@task_router_tms.delete("/task/{task_id}")
def delete_existing_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)   
    db.commit() 
    return {"message": "Task deleted successfully"}

# Example: Filter tasks by priority
@task_router_tms.get("/tasks/search", response_model=List[TaskResponse])
def search_tasks(
    priority: Optional[PriorityEnum] = None,
    due_date: Optional[str] = None,
    status: Optional[StatusEnum] = None,
    keyword: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filters = [Task.user_id == current_user.id]
    
    if priority is not None:
        filters.append(Task.priority == priority)
    
    if due_date is not None:
        today = datetime.today().date()
        if due_date == "Today":
            filters.append(Task.due_date == today)
        elif due_date == "This week":
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            filters.append(Task.due_date.between(start_of_week, end_of_week))
        elif due_date == "Overdue":
            filters.append(Task.due_date < today)
        else:
            try:
                search_date = datetime.fromisoformat(due_date.replace("Z", "+00:00")).date()
                filters.append(Task.due_date == search_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
    
    if status is not None:
        filters.append(Task.status == status)
    
    if keyword is not None:
        # Case-insensitive search in title or description
        filters.append(or_(
            Task.title.ilike(f"%{keyword}%"),
            Task.description.ilike(f"%{keyword}%")
        ))
    
    tasks = db.query(Task).filter(and_(*filters)).all()
    return tasks