from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
import shutil

from ..database import get_db
from .. import models, schemas

# Directory where uploaded images will be stored
UPLOAD_DIR = Path("uploads")

# Maximum allowed file size in megabytes
MAX_FILE_SIZE_MB = 10

# MIME types accepted for upload
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}

# ============================================================================
# Setup
# ============================================================================

# Create upload directory if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize router with prefix and tags for API documentation
router = APIRouter(
    prefix="/api/images",
    tags=["Uploads"]
)


# ============================================================================
# Helper Functions
# ============================================================================

def validate_file_type(content_type: str) -> None:
    """
    Validate that the uploaded file is an allowed image type.
    
    Args:
        content_type: MIME type of the uploaded file
        
    Raises:
        HTTPException: If file type is not allowed
    """
    if content_type not in ALLOWED_IMAGE_TYPES:
        allowed_types = ", ".join(ALLOWED_IMAGE_TYPES)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {allowed_types}"
        )


def validate_file_size(file_size: int) -> None:
    """
    Validate that the file size doesn't exceed the maximum allowed.
    
    Args:
        file_size: Size of the file in bytes
        
    Raises:
        HTTPException: If file size exceeds the limit
    """
    # Convert MB to bytes for comparison
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
        )


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename while preserving the original extension.
    
    This prevents filename collisions and potential security issues
    from user-provided filenames.
    
    Args:
        original_filename: Original name of the uploaded file
        
    Returns:
        A unique filename with the original extension
    """
    # Extract file extension (e.g., ".jpg")
    file_extension = Path(original_filename).suffix
    
    # Generate unique filename using UUID hex string
    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    
    return unique_name


def save_file_to_disk(file: UploadFile, filepath: Path) -> None:
    """
    Save the uploaded file to the specified path on disk.
    
    Args:
        file: FastAPI UploadFile object
        filepath: Destination path where file will be saved
    """
    # Open destination file and copy uploaded content
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def create_image_record(db: Session, filename: str, content_type: str, 
                        file_size: int, filepath: str) -> models.Image:
    """
    Create and save an image record to the database.
    
    Args:
        db: Database session
        filename: Name of the saved file
        content_type: MIME type of the file
        file_size: Size of the file in bytes
        filepath: Full path where file is stored
        
    Returns:
        The created Image model instance with database-generated fields
    """
    # Create new image record
    image = models.Image(
        filename=filename,
        content_type=content_type,
        size=file_size,
        path=filepath,
    )
    
    # Save to database
    db.add(image)
    db.commit()
    
    # Refresh to get auto-generated fields (id, timestamps, etc.)
    db.refresh(image)
    
    return image


# ============================================================================
# API Endpoints
# ============================================================================

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ImageUploadResponse
)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an image file.
    
    Validates file type and size, saves the file to disk,
    and stores metadata in the database.
    
    Args:
        file: The uploaded image file
        db: Database session (injected by FastAPI)
        
    Returns:
        ImageUploadResponse with success message and file metadata
        
    Raises:
        HTTPException: If validation fails (invalid type or size)
    """
    # Step 1: Validate file type
    validate_file_type(file.content_type)
    
    # Step 2: Read file content and validate size
    file_content = await file.read()
    validate_file_size(len(file_content))
    
    # Step 3: Reset file pointer to beginning after reading
    # This is necessary because we need to read the file again when saving
    await file.seek(0)
    
    # Step 4: Generate unique filename and construct full path
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename
    
    # Step 5: Save file to disk
    save_file_to_disk(file, file_path)
    
    # Step 6: Save metadata to database
    image_record = create_image_record(
        db=db,
        filename=unique_filename,
        content_type=file.content_type,
        file_size=len(file_content),
        filepath=str(file_path)
    )
    
    # Step 7: Return success response with metadata
    return schemas.ImageUploadResponse(
        message="Upload successful",
        metadata=image_record
    )