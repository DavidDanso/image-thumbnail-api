from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import uuid

###################### USER MODEL
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    
    images = relationship("Image", back_populates="owner")

###################### IMAGE MODEL
class Image(Base):
    __tablename__ = "images"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, unique=True, index=True)
    content_type = Column(String)
    size = Column(Integer)
    path = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    owner = relationship("User", back_populates="images")
    thumbnails = relationship("Thumbnail", back_populates="image")

###################### THUMBNAIL MODEL
class Thumbnail(Base):
    __tablename__ = "thumbnails"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    path = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    
    image = relationship("Image", back_populates="thumbnails")