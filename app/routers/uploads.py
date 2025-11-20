from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import shutil

from ..database import get_db
from .. import models, schemas, oauth2


# Configuration
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE_MB = 10
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", 
                 "image/svg+xml", "image/heic", "image/heif", "image/avif"}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Router setup
router = APIRouter(prefix="/api/images", tags=["Uploads"])


# ============================================================================
# Validation Functions
# ============================================================================

def validate_image(file: UploadFile, content: bytes) -> None:
    """
    Validate uploaded file type and size.
    
    Args:
        file: Uploaded file object
        content: File content as bytes
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_TYPES)}"
        )
    
    # Check file size
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit"
        )


def generate_filename(original_filename: str) -> str:
    """
    Generate unique filename preserving original extension.
    
    Args:
        original_filename: Original file name
        
    Returns:
        Unique filename with UUID prefix
    """
    extension = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{extension}"


# ============================================================================
# File Operations
# ============================================================================

def save_image(file: UploadFile, filepath: Path) -> None:
    """
    Save uploaded file to disk.
    
    Args:
        file: Uploaded file object
        filepath: Destination path
    """
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def create_db_record(
    db: Session,
    filename: str,
    content_type: str,
    file_size: int,
    filepath: str,
    owner_id: int
) -> models.Image:
    """
    Create image record in database.
    
    Args:
        db: Database session
        filename: Saved filename
        content_type: MIME type
        file_size: File size in bytes
        filepath: Full file path
        
    Returns:
        Created image record
    """
    image = models.Image(
        filename=filename,
        content_type=content_type,
        size=file_size,
        path=filepath,
        owner_id=owner_id
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


# ============================================================================
# API Endpoint
# ============================================================================

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ImageUploadResponse
)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Upload and store an image file.
    
    Validates file type and size, saves to disk, stores metadata in database.
    
    Returns:
        Success message with file metadata
    """
    # Read file content once
    content = await file.read()
    
    # Validate file
    validate_image(file, content)
    
    # Generate unique filename
    filename = generate_filename(file.filename)
    filepath = UPLOAD_DIR / filename
    
    # Reset file pointer for saving
    await file.seek(0)
    
    # Save file to disk
    save_image(file, filepath)
    
    # Save metadata to database
    image_record = create_db_record(
        db=db,
        filename=filename,
        content_type=file.content_type,
        file_size=len(content),
        filepath=str(filepath),
        owner_id=current_user.id
    )
    
    return schemas.ImageUploadResponse(
        message="Image uploaded successfully",
        metadata=image_record
    )