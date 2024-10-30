import os
import logging
from werkzeug.utils import secure_filename
from google.cloud import vision
import io
import cv2
import numpy as np
import mediapipe as mp
from datetime import datetime
import json

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads'

# Initialize MediaPipe pose detection with error handling
try:
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    logger.info("MediaPipe pose detection initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MediaPipe pose detection: {str(e)}")
    pose = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists and is writable"""
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        # Test write permissions
        test_file = os.path.join(UPLOAD_FOLDER, '.test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        logger.error(f"Upload folder setup failed: {str(e)}")
        return False

def enhance_image(image_path):
    """Enhance image quality and handle lighting conditions with improved error handling"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to read image: {image_path}")
            return None

        # Convert to LAB color space
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        # Merge channels
        enhanced_lab = cv2.merge((cl,a,b))
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

        # Save enhanced image
        enhanced_path = f"{image_path.rsplit('.', 1)[0]}_enhanced.{image_path.rsplit('.', 1)[1]}"
        success = cv2.imwrite(enhanced_path, enhanced_bgr)
        
        if not success:
            logger.error(f"Failed to save enhanced image: {enhanced_path}")
            return None
            
        return enhanced_path
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        return None

def detect_pose(image_path):
    """Detect human poses in the image with improved initialization checks"""
    if pose is None:
        logger.error("Pose detection is not initialized")
        return None
        
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to read image for pose detection: {image_path}")
            return None

        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = pose.process(image_rgb)
        
        if results.pose_landmarks:
            # Convert landmarks to normalized coordinates
            pose_data = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                pose_data[f"landmark_{idx}"] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                }
            return pose_data
        return None
    except Exception as e:
        logger.error(f"Error detecting pose: {str(e)}")
        return None

def verify_pose(pose_data, required_pose):
    """Verify if the detected pose matches the required pose with improved validation"""
    if not pose_data:
        logger.warning("No pose data provided for verification")
        return False, 0.0

    try:
        # Define pose verification logic based on required_pose
        if required_pose == "hands_up":
            # Check if hands are above head
            left_wrist = pose_data.get("landmark_15")  # Left wrist
            right_wrist = pose_data.get("landmark_16")  # Right wrist
            nose = pose_data.get("landmark_0")  # Nose
            
            if all([left_wrist, right_wrist, nose]):
                if left_wrist['y'] < nose['y'] and right_wrist['y'] < nose['y']:
                    confidence = min(left_wrist['visibility'], right_wrist['visibility'])
                    return True, confidence
                    
        elif required_pose == "t_pose":
            # Check if arms are horizontal
            left_shoulder = pose_data.get("landmark_11")
            right_shoulder = pose_data.get("landmark_12")
            left_wrist = pose_data.get("landmark_15")
            right_wrist = pose_data.get("landmark_16")
            
            if all([left_shoulder, right_shoulder, left_wrist, right_wrist]):
                shoulder_height = (left_shoulder['y'] + right_shoulder['y']) / 2
                wrist_height_diff = abs(left_wrist['y'] - right_wrist['y'])
                
                if wrist_height_diff < 0.1 and abs(left_wrist['y'] - shoulder_height) < 0.1:
                    confidence = min(left_wrist['visibility'], right_wrist['visibility'])
                    return True, confidence

        return False, 0.0
    except Exception as e:
        logger.error(f"Error verifying pose: {str(e)}")
        return False, 0.0

def save_photo(photo_file):
    """Save the uploaded photo with improved error handling"""
    if not ensure_upload_folder():
        raise RuntimeError("Failed to setup upload folder")
        
    try:
        filename = secure_filename(photo_file.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        photo_file.save(filepath)
        
        # Verify the file was saved
        if not os.path.exists(filepath):
            raise RuntimeError(f"Failed to save file: {filepath}")
            
        return filepath
    except Exception as e:
        logger.error(f"Error saving photo: {str(e)}")
        raise

def verify_photo_content(photo_path, required_objects, min_confidence=0.7, required_pose=None, required_location=None):
    """Verify photo content with improved error handling and validation"""
    if not os.path.exists(photo_path):
        logger.error(f"Photo file not found: {photo_path}")
        return False, 0.0

    try:
        # Convert single object to list
        if isinstance(required_objects, str):
            required_objects = [required_objects]

        # Enhance image quality
        enhanced_path = enhance_image(photo_path) or photo_path

        # Initialize Vision client
        client = vision.ImageAnnotatorClient()

        with io.open(enhanced_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        
        # Detect objects
        objects = client.object_localization(image=image).localized_object_annotations
        
        # Check for required objects
        found_objects = {}
        for required_obj in required_objects:
            found_objects[required_obj] = False
            max_confidence = 0.0
            
            for obj in objects:
                if required_obj.lower() in obj.name.lower():
                    found_objects[required_obj] = True
                    max_confidence = max(max_confidence, obj.score)
                    
        # Calculate overall object detection confidence
        object_results = {
            'all_found': all(found_objects.values()),
            'confidence': min([obj.score for obj in objects if any(req.lower() in obj.name.lower() for req in required_objects)] or [0.0])
        }

        # Check pose if required
        pose_results = {'verified': True, 'confidence': 1.0}
        if required_pose:
            pose_data = detect_pose(photo_path)
            pose_verified, pose_confidence = verify_pose(pose_data, required_pose)
            pose_results = {'verified': pose_verified, 'confidence': pose_confidence}

        # Check location if required
        location_results = {'verified': True, 'confidence': 1.0}
        if required_location:
            # Get image location data
            location_info = client.landmark_detection(image=image).landmark_annotations
            location_verified = any(
                required_location.lower() in landmark.description.lower()
                for landmark in location_info
            )
            location_confidence = max(
                (landmark.score for landmark in location_info 
                if required_location.lower() in landmark.description.lower()),
                default=0.0
            )
            location_results = {'verified': location_verified, 'confidence': location_confidence}

        # Calculate overall verification result
        is_verified = (
            object_results['all_found'] and
            pose_results['verified'] and
            location_results['verified']
        )

        # Calculate overall confidence score
        confidence_score = min(
            object_results['confidence'],
            pose_results['confidence'],
            location_results['confidence']
        )

        return is_verified, confidence_score

    except Exception as e:
        logger.error(f"Error in photo verification: {str(e)}")
        return False, 0.0

def cleanup_old_photos(days_old=7):
    """Remove photos older than specified days with improved error handling"""
    if not os.path.exists(UPLOAD_FOLDER):
        logger.warning(f"Upload folder does not exist: {UPLOAD_FOLDER}")
        return
        
    try:
        current_time = datetime.now()
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                if (current_time - file_modified).days > days_old:
                    os.remove(filepath)
                    logger.info(f"Removed old photo: {filename}")
            except OSError as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error cleaning up old photos: {str(e)}")
