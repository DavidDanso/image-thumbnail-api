from typing import List
from fastapi import Depends, HTTPException, APIRouter, status, Response
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from .. database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=['Users']
)


###################### profile { READ } #####################
@router.get("/me", response_model=schemas.UserResponse)
def get_profile(db: Session = Depends(get_db), 
              get_user: int = Depends(oauth2.get_current_user)):

    return get_user


###################### get user by ID { READ } #####################
@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db), 
             get_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User with ID: {id} not found")

    return user


###################### update user by ID { UPDATE } #####################
@router.put("/{id}", response_model=schemas.UserResponse)
def update_user(id: int, user: schemas.UserCreate, db: Session = Depends(get_db), 
                get_user: int = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)

    if user_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User with ID: {id} not found")
    
    user_query.update(user.model_dump(), synchronize_session=False)
    db.commit()

    return user_query.first()


###################### delete user by ID { DELETE } #####################
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), 
                get_user: int = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)

    if user_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User with ID: {id} not found")
    
    user_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


