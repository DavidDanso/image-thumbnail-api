from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, Integer, String, func, text
from .database import Base
from sqlalchemy.orm import relationship


###################### USER MODEL
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)


###################### IMAGE MODEL
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    content_type = Column(String)
    size = Column(Integer)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    path = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)



# class Task(Base):
#     __tablename__ = "tasks"

#     id = Column(Integer, primary_key=True, nullable=False)
#     title = Column(String, nullable=False)
#     description = Column(String, nullable=False)
#     status = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
#     owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     owner = relationship("User")