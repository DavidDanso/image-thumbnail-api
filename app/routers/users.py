from uuid import UUID
from fastapi import Depends, HTTPException, APIRouter, status, Response
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=['Users']
)

###################### profile { READ } #####################
@router.get("/me", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(oauth2.get_current_user)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                          detail="User not found")

    return current_user

###################### update user { UPDATE } #####################
@router.put("/{id}", response_model=schemas.UserResponse)
def update_user(id: UUID, user_update: schemas.UserCreate,
                db: Session = Depends(get_db), 
                current_user: models.User = Depends(oauth2.get_current_user)):
    # Authorization check
    if current_user.id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                          detail="Not authorized to update this user")
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                          detail="User not found")
    
    # Only update allowed fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Hash password if being updated
    if "password" in update_data:
        update_data["password"] = utils.hash_password(update_data["password"])
    
    user_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(user)
    return user

###################### delete user { DELETE } #####################
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: UUID, db: Session = Depends(get_db), 
                current_user: models.User = Depends(oauth2.get_current_user)):
    # Authorization check
    if current_user.id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                          detail="Not authorized to delete this user")
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                          detail="User not found")
    
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)