from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Dict, List, Any, Optional

# Database connection
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
    max_uses = Column(Integer, nullable=True)
    weight = Column(Float, default=0.0)

class Container(Base):
    __tablename__ = "containers"
    
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    zone = Column(String)
    dimensions = Column(JSON)  # width, depth, height
    max_weight = Column(Float, default=0.0)

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String)  # search, retrieve, place, etc.
    user_id = Column(String)
    item_id = Column(String)
    item_name = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)  # Additional details as JSON

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database operations for items
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
        "usage_count": item.usage_count,
        "max_uses": item.max_uses,
        "weight": item.weight
    }

def get_item_by_name(db: Session, item_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a single item by exact name.
    """
    item = db.query(Item).filter(Item.name == item_name).first()
    if not item:
        return None
    
    return {
        "id": item.id,
        "name": item.name,
        "container_id": item.container_id,
        "zone": item.zone,
        "position": item.position,
        "expiry_date": item.expiry_date,
        "usage_count": item.usage_count,
        "max_uses": item.max_uses,
        "weight": item.weight
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
            "usage_count": item.usage_count,
            "max_uses": item.max_uses,
            "weight": item.weight
        }
        for item in items
    ]

def get_all_items(db: Session) -> List[Dict[str, Any]]:
    """
    Get all items from the database.
    """
    items = db.query(Item).all()
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "container_id": item.container_id,
            "zone": item.zone,
            "position": item.position,
            "expiry_date": item.expiry_date,
            "usage_count": item.usage_count,
            "max_uses": item.max_uses,
            "weight": item.weight
        }
        for item in items
    ]

def create_item(db: Session, item_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new item in the database.
    """
    item = Item(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return {
        "id": item.id,
        "name": item.name,
        "container_id": item.container_id,
        "zone": item.zone,
        "position": item.position,
        "expiry_date": item.expiry_date,
        "usage_count": item.usage_count,
        "max_uses": item.max_uses,
        "weight": item.weight
    }

def update_item_position(db: Session, item_id: str, container_id: str, position: Dict[str, Any]) -> None:
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
        item.usage_count += 1
        db.commit()

def remove_items_from_inventory(db: Session, item_ids: List[str]) -> int:
    """
    Remove items from inventory by their IDs.
    Returns the number of items removed.
    """
    count = db.query(Item).filter(Item.id.in_(item_ids)).delete(synchronize_session=False)
    db.commit()
    return count

# Database operations for containers
def get_container_by_id(db: Session, container_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a container by its ID.
    """
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        return None
    
    return {
        "id": container.id,
        "name": container.name,
        "zone": container.zone,
        "dimensions": container.dimensions,
        "max_weight": container.max_weight
    }

def get_all_containers(db: Session) -> List[Dict[str, Any]]:
    """
    Get all containers from the database.
    """
    containers = db.query(Container).all()
    
    return [
        {
            "id": container.id,
            "name": container.name,
            "zone": container.zone,
            "dimensions": container.dimensions,
            "max_weight": container.max_weight
        }
        for container in containers
    ]

def create_container(db: Session, container_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new container in the database.
    """
    container = Container(**container_data)
    db.add(container)
    db.commit()
    db.refresh(container)
    
    return {
        "id": container.id,
        "name": container.name,
        "zone": container.zone,
        "dimensions": container.dimensions,
        "max_weight": container.max_weight
    }

def get_items_by_container(db: Session, container_id: str) -> List[Dict[str, Any]]:
    """
    Get all items in a specific container.
    """
    items = db.query(Item).filter(Item.container_id == container_id).all()
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "container_id": item.container_id,
            "zone": item.zone,
            "position": item.position,
            "expiry_date": item.expiry_date,
            "usage_count": item.usage_count,
            "max_uses": item.max_uses,
            "weight": item.weight
        }
        for item in items
    ]

# Logging operations
def log_action(
    db: Session, 
    action_type: str, 
    user_id: str, 
    item_id: str, 
    item_name: Optional[str] = None,
    timestamp: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an action in the database.
    """
    log_entry = ActionLog(
        action_type=action_type,
        user_id=user_id,
        item_id=item_id,
        item_name=item_name,
        details=details
    )
    
    if timestamp:
        try:
            log_entry.timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            # If timestamp is invalid, use current time
            pass
    
    db.add(log_entry)
    db.commit()

def get_logs(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    item_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get logs filtered by various criteria.
    """
    query = db.query(ActionLog)
    
    if start_date:
        query = query.filter(ActionLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(ActionLog.timestamp <= end_date)
    
    if item_id:
        query = query.filter(ActionLog.item_id == item_id)
    
    if user_id:
        query = query.filter(ActionLog.user_id == user_id)
    
    if action_type:
        query = query.filter(ActionLog.action_type == action_type)
    
    logs = query.order_by(ActionLog.timestamp.desc()).all()
    
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "action_type": log.action_type,
            "user_id": log.user_id,
            "item_id": log.item_id,
            "item_name": log.item_name,
            "details": log.details
        }
        for log in logs
    ]

