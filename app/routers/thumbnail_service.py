from PIL import Image as PILImage
from pathlib import Path
import uuid

def generate_thumbnail(
    source_path: str,
    output_path: str,
    width: int,
    height: int
) -> tuple[int, int]:
    """
    Generate thumbnail from source image.
    Returns actual (width, height) of generated thumbnail.
    """
    # Open original image
    with PILImage.open(source_path) as img:
        # Convert RGBA to RGB if needed (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize maintaining aspect ratio
        img.thumbnail((width, height), PILImage.Resampling.LANCZOS)
        
        # Save thumbnail
        img.save(output_path, 'JPEG', quality=95, optimize=True)
        
        # Return actual dimensions
        return img.size