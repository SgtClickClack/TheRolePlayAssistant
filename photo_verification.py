import os
import logging
from werkzeug.utils import secure_filename
from google.cloud import vision
import io

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(photo_file):
    """Save the uploaded photo and return the file path."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    filename = secure_filename(photo_file.filename)
    unique_filename = f"{os.urandom(8).hex()}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    photo_file.save(filepath)
    return filepath

def verify_photo_content(photo_path, required_object, min_confidence=0.7):
    """
    Verify if the photo contains the required object using Google Cloud Vision API.
    Returns (is_verified, confidence_score)
    """
    try:
        client = vision.ImageAnnotatorClient()

        with io.open(photo_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        objects = client.object_localization(image=image).localized_object_annotations
        
        # Check if any detected object matches the required object
        for obj in objects:
            if required_object.lower() in obj.name.lower():
                if obj.score >= min_confidence:
                    return True, obj.score
                
        # If no matching object found with sufficient confidence
        return False, 0.0
        
    except Exception as e:
        logger.error(f"Error in photo verification: {str(e)}")
        return False, 0.0

def cleanup_old_photos(days_old=7):
    """Remove photos older than specified days to manage storage."""
    try:
        current_time = datetime.now()
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            if (current_time - file_modified).days > days_old:
                os.remove(filepath)
                logger.info(f"Removed old photo: {filename}")
    except Exception as e:
        logger.error(f"Error cleaning up old photos: {str(e)}")
