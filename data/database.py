from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Dict, List, Any, Optional

# This would be replaced with a real database connection
DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class Item(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    container_id = Column(String, index=True)
    zone = Column(String)
    position = Column(JSON)  # Stores the position as JSON
    expiry_date = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String)  # search, retrieve, place
    user_id = Column(String)
    item_id = Column(String)
    item_name = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database operations
def get_item_by_id(db: Session, item_id: str) -> Optional[Dict[str, Any]]:
    """
    Get an item by its ID.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return None
    
    return {
        "id": item.id,
        "name": item.name,
        "container_id": item.container_id,
        "zone": item.zone,
        "position": item.position,
        "expiry_date": item.expiry_date,
        "usage_count": item.usage_count
    }

def get_items_by_name(db: Session, item_name: str) -> List[Dict[str, Any]]:
    """
    Get items by name (can return multiple items).
    """
    items = db.query(Item).filter(Item.name.like(f"%{item_name}%")).all()
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "container_id": item.container_id,
            "zone": item.zone,
            "position": item.position,
            "expiry_date": item.expiry_date,
            "usage_count": item.usage_count
        }
        for item in items
    ]

def log_action(
    db: Session, 
    action_type: str, 
    user_id: str, 
    item_id: str, 
    item_name: Optional[str] = None,
    timestamp: Optional[str] = None
) -> None:
    """
    Log an action in the database.
    """
    log_entry = ActionLog(
        action_type=action_type,
        user_id=user_id,
        item_id=item_id,
        item_name=item_name
    )
    
    if timestamp:
        try:
            log_entry.timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            # If timestamp is invalid, use current time
            pass
    
    db.add(log_entry)
    db.commit()

def update_item_position(
    db: Session, 
    item_id: str, 
    container_id: str, 
    position: Dict[str, Any]
) -> None:
    """
    Update an item's position and container.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.container_id = container_id
        item.position = position
        db.commit()

def update_item_usage(db: Session, item_id: str) -> None:
    """
    Increment the usage count of an item.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.

