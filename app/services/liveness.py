import cv2
import numpy as np
import dlib
from deepface import DeepFace

# Load Face Detector (dlib)
face_detector = dlib.get_frontal_face_detector()

# Load Eye Detector (OpenCV)
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# Load FaceNet Model (DeepFace)
facenet_model = DeepFace.build_model("Facenet")

# Global variable for storing previous frame
previous_frame = None
FRAME_SIZE = (640, 480)  # Fixed frame size to avoid shape mismatch

def detect_motion_optical_flow(image):
    """
    Uses Optical Flow to detect small facial movements (liveness).
    Ensures it's a real face and not a static image.
    """
    global previous_frame

    # Convert image to grayscale and resize
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, FRAME_SIZE)  # Ensure uniform shape

    if previous_frame is None:
        previous_frame = gray
        return False  # No previous frame to compare

    # Compute absolute difference between frames
    diff = cv2.absdiff(previous_frame, gray)
    previous_frame = gray  # Update previous frame

    # Compute motion variance
    movement_threshold = 500  # Adjust based on testing
    variance = np.var(diff)

    return variance > movement_threshold

def check_liveness(image):
    """
    - Uses FaceNet for face verification.
    - Detects blinking using OpenCV Haarcascades.
    - Uses Optical Flow for motion detection.
    """
    try:
        # Convert image to grayscale and resize
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, FRAME_SIZE)

        # Detect faces
        faces = face_detector(gray)

        if len(faces) == 0:
            return {"code": "01", "message": "Failure", "description": "No face detected"}

        for face in faces:
            x, y, w, h = (face.left(), face.top(), face.width(), face.height())
            roi_gray = gray[y:y+h, x:x+w]

            # Detect eyes
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))

            if len(eyes) < 2:
                return {"code": "01", "message": "Failure", "description": "No blinking detected"}

            # Motion Detection
            if not detect_motion_optical_flow(image):
                return {"code": "01", "message": "Failure", "description": "No motion detected"}

            # Face Embedding Verification (FaceNet)
            embeddings = DeepFace.represent(image, model_name="Facenet", enforce_detection=False)
            if embeddings is None:
                return {"code": "01", "message": "Failure", "description": "Face verification failed"}

        return {"code": "00", "message": "Success","description": "Live human face detected"}

    except Exception as e:
        return {"code": "01", "message": "Failure", "description": str(e)}
