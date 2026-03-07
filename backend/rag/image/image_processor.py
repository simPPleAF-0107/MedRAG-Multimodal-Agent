import io
from PIL import Image

class ImageProcessor:
    """
    Handles preprocessing of images (e.g., resizing, formatting)
    before they are embedded by the CLIP model.
    """
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
        """
        Convert raw image bytes into a PIL Image object.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB to ensure consistency, especially if RGBA or grayscale
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise ValueError(f"Failed to load image from bytes: {e}")
            
    @staticmethod
    def load_image_from_path(file_path: str) -> Image.Image:
        """
        Load a PIL Image from a local file path.
        """
        try:
            image = Image.open(file_path)
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise ValueError(f"Failed to load image from path {file_path}: {e}")

image_processor = ImageProcessor()
