from typing import List
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

###################### USER SCEHMAS
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: UUID
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


###################### THUMBNAIL SCHEMAS
class ThumbnailResponse(BaseModel):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

###################### IMAGE SCHEMAS
class ImageMetadataResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size: int
    path: str
    owner: UserResponse
    thumbnails: List[ThumbnailResponse]
    
    class Config:
        from_attributes = True

class ImageUploadResult(BaseModel):
    image_id: UUID
    thumbnail_id: UUID
    thumbnail_status: str

# class ImageUploadResponse(BaseModel):
#     message: str
#     metadata: ImageMetadataResponse