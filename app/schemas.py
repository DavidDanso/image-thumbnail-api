from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

###################### USER SCEHMAS
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


    
###################### LOGIN SCEHMAS
class UserLogin(BaseModel):
    email: EmailStr
    password: str


###################### TOKEN SCEHMAS
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str 



###################### IMAGE SCHEMAS
class ImageMetadataResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    path: str
    upload_time: datetime
    
    class Config:
        from_attributes = True

class ImageUploadResponse(BaseModel):
    message: str
    metadata: ImageMetadataResponse
