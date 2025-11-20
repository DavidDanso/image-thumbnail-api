from fastapi import Depends, HTTPException, APIRouter, status, Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import models, schemas, utils, oauth2
from .. database import get_db

router = APIRouter(
    prefix="/api/auth",
    tags=['Authentication']
)

###################### create new USER { CREATE } #####################
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    existing_username = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail=f"Username '{user.username}' is already taken")
    
    # Check if email exists
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail=f"Email '{user.email}' is already registered")
    
    
    hash_password = utils.get_password_hash(user.password) 
    user.password = hash_password
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


###################### login user { CREATE } #####################
@router.post("/login", response_model=schemas.Token)
def login_user(user_crendential: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_crendential.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"Invalid User Credential")
    
    if not utils.verify_password(user_crendential.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"Invalid User Credential")
    
    access_token = oauth2.create_access_token(data={"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}





