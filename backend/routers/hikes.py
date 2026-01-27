from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.hike import Hike
from schemas.hike import HikeCreate, HikeUpdate, HikeResponse

router = APIRouter()

@router.get("", response_model=List[HikeResponse])
def get_hikes(
    skip: int = 0,
    limit: int = 100,
    difficulty: str = None,
    db: Session = Depends(get_db)
):
    """Get all hikes with optional filtering"""
    query = db.query(Hike)
    
    if difficulty:
        query = query.filter(Hike.difficulty == difficulty)
    
    hikes = query.offset(skip).limit(limit).all()
    return hikes

@router.get("/{hike_id}", response_model=HikeResponse)
def get_hike(hike_id: int, db: Session = Depends(get_db)):
    """Get a specific hike by ID"""
    hike = db.query(Hike).filter(Hike.id == hike_id).first()
    if not hike:
        raise HTTPException(status_code=404, detail="Hike not found")
    return hike

@router.post("", response_model=HikeResponse, status_code=201)
def create_hike(hike: HikeCreate, db: Session = Depends(get_db)):
    """Create a new hike"""
    db_hike = Hike(**hike.model_dump())
    db.add(db_hike)
    db.commit()
    db.refresh(db_hike)
    return db_hike

@router.put("/{hike_id}", response_model=HikeResponse)
def update_hike(hike_id: int, hike: HikeUpdate, db: Session = Depends(get_db)):
    """Update an existing hike"""
    db_hike = db.query(Hike).filter(Hike.id == hike_id).first()
    if not db_hike:
        raise HTTPException(status_code=404, detail="Hike not found")
    
    update_data = hike.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_hike, key, value)
    
    db.commit()
    db.refresh(db_hike)
    return db_hike

@router.delete("/{hike_id}", status_code=204)
def delete_hike(hike_id: int, db: Session = Depends(get_db)):
    """Delete a hike"""
    db_hike = db.query(Hike).filter(Hike.id == hike_id).first()
    if not db_hike:
        raise HTTPException(status_code=404, detail="Hike not found")
    
    db.delete(db_hike)
    db.commit()
    return None
