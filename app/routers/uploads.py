from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import shutil

from ..database import get_db
from .. import models, schemas, oauth2
from .thumbnail_service import generate_thumbnail


# Configuration
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE_MB = 10
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", 
                 "image/svg+xml", "image/heic", "image/heif", "image/avif"}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR = Path("uploads/thumbnails")
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

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

def save_image(content: bytes, filepath: Path) -> None:
    """
    Save uploaded file to disk.
    
    Args:
        content: File content in bytes
        filepath: Destination path
    """
    with open(filepath, "wb") as buffer:
        buffer.write(content)


def create_db_record(
    db: Session,
    filename: str,
    content_type: str,
    file_size: int,
    filepath: str,
    owner_id: uuid.UUID
) -> models.Image:
    """
    Create image record in database.
    
    Args:
        db: Database session
        filename: Saved filename
        content_type: MIME type
        file_size: File size in bytes
        filepath: Full file path
        owner_id: ID of the user uploading the image
    """
    db_image = models.Image(
        filename=filename,
        content_type=content_type,
        size=file_size,
        path=filepath,
        owner_id=owner_id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def create_thumbnail_background(
    db: Session,
    image_id: uuid.UUID,
    image_path: str,
    thumbnail_id: uuid.UUID,
    width: int,
    height: int
):
    """
    Background task to generate thumbnail and update DB.
    """
    try:
        # Generate unique filename
        thumbnail_filename = f"{image_id}_thumb_{width}x{height}.jpg"
        thumbnail_path = THUMBNAIL_DIR / thumbnail_filename
        
        # Generate thumbnail
        actual_width, actual_height = generate_thumbnail(
            source_path=image_path,
            output_path=str(thumbnail_path),
            width=width,
            height=height
        )
        
        # Update DB: mark as ready
        thumbnail = db.query(models.Thumbnail).filter(
            models.Thumbnail.id == thumbnail_id
        ).first()
        
        if thumbnail:
            thumbnail.status = "ready"
            thumbnail.path = str(thumbnail_path)
            thumbnail.width = actual_width
            thumbnail.height = actual_height
            db.commit()
    
    except Exception as e:
        # If failed, mark as failed
        thumbnail = db.query(models.Thumbnail).filter(
            models.Thumbnail.id == thumbnail_id
        ).first()
        
        if thumbnail:
            thumbnail.status = "failed"
            db.commit()
        
        print(f"Thumbnail generation failed: {e}")


# ============================================================================
# Uploads and Thumbnails Endpoint
# ============================================================================
@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ImageUploadResult
)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    """
    Upload image and trigger thumbnail generation.
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    
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
    
    # Save file to disk
    save_image(content, filepath)
    
    # Save metadata to database
    image_record = create_db_record(
        db=db,
        filename=filename,
        content_type=file.content_type,
        file_size=len(content),
        filepath=str(filepath),
        owner_id=current_user.id
    )

    # Create Thumbnail record (pending)
    thumbnail_width = 500
    thumbnail_height = 500
    
    db_thumbnail = models.Thumbnail(
        image_id=image_record.id,
        width=thumbnail_width,
        height=thumbnail_height,
        status="pending"
    )
    db.add(db_thumbnail)
    db.commit()
    db.refresh(db_thumbnail)
    
    # Trigger background task
    background_tasks.add_task(
        create_thumbnail_background,
        db=db,
        image_id=image_record.id,
        image_path=str(filepath),
        thumbnail_id=db_thumbnail.id,
        width=thumbnail_width,
        height=thumbnail_height
    )
    
    return {
        "image_id": image_record.id,
        "thumbnail_id": db_thumbnail.id,
        "thumbnail_status": "pending"
    }


###################### all uploads { READ } #####################
@router.get("/upload", response_model=list[schemas.ImageMetadataResponse])
def get_uploads(db: Session = Depends(get_db), 
              current_user: models.User = Depends(oauth2.get_current_user)):
    
    all_uploads = db.query(models.Image).filter(models.Image.owner_id == current_user.id).all()
    return all_uploads


###################### get image metadata by ID { READ } #####################
@router.get("/{id}", response_model=schemas.ImageMetadataResponse)
def get_image_metadata(
    id: uuid.UUID, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Get metadata for a specific image by ID.
    """
    image = db.query(models.Image).filter(models.Image.id == id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this image"
        )

    return image


###################### download image { READ } #####################
@router.get("/{id}/file", response_model=schemas.ImageMetadataResponse)
async def download_image(
    id: uuid.UUID, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Get metadata for a specific image by ID.
    """
    image = db.query(models.Image).filter(models.Image.id == id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this image"
        )

    # 3. Check file exists
    file_path = Path(image.path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on server"
        )
    
    # Destination path in downloads folder
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)
    dest_path = download_dir / file_path.name

    # Copy file to downloads folder
    shutil.copyfile(str(file_path), str(dest_path))

    # 4. Return file
    return FileResponse(
        path=str(dest_path),
        media_type=image.content_type,
        filename=image.filename,
        headers={
            "Content-Disposition": f"attachment; filename={image.filename}"
        }
    )

###################### get image metadata by ID { DELETE } #####################
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    id: uuid.UUID, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Delete a specific image by ID.
    """
    image_query = db.query(models.Image).filter(models.Image.id == id)
    image = image_query.first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this image"
        )

    image_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    
###################### thumbnail status { READ } #####################
@router.get("/thumbnails/{thumbnail_id}")
def get_thumbnail_status(
    thumbnail_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Check thumbnail generation status.
    """
    thumbnail = db.query(models.Thumbnail).filter(
        models.Thumbnail.id == thumbnail_id
    ).first()
    
    if not thumbnail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found"
        )
    
    if thumbnail.image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this thumbnail"
        )
    
    return {
        "id": thumbnail.id,
        "image_id": thumbnail.image_id,
        "status": thumbnail.status,
        "width": thumbnail.width,
        "height": thumbnail.height,
        "path": thumbnail.path
    }