import os
import shutil
import json
from datetime import datetime
from app.services.liveness import check_liveness
import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.services.database import execute_query, fetch_all, execute_query_with_output
from deepface import DeepFace

# Define the storage directory
IMAGE_FOLDER = "images/faces/"
# Ensure the folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)
router = APIRouter(prefix="/face-recognition", tags=["Face Recognition"])
# ✅ Function to Extract Face Embedding
def extract_face_embedding(image_path: str) -> list:
    """Extracts face embedding using DeepFace and returns it as a list."""
    try:
        embedding = DeepFace.represent(img_path=image_path, model_name="Facenet")[0]["embedding"]
        return embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting face embedding: {str(e)}")


# ✅ Function to Save or Update Image
def save_face_image(employee_id: int, image_file: UploadFile, created_by: str) -> str:
    """Saves or updates an uploaded face image for a specific user and returns its path."""
    # Define the user's folder path
    employee_folder = os.path.join(IMAGE_FOLDER, f"employee_{employee_id}")
    os.makedirs(employee_folder, exist_ok=True)  # Create folder if not exists

    # Define the full image path
    image_path = os.path.join(employee_folder, image_file.filename)
    image_path = os.path.normpath(image_path)  # Normalize the file path to handle OS-specific issues

    # Check if the file exists
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    return image_path

# API endpoint to save face image and embedding
@router.post("/save-face")
async def save_face(
    employee_id: int = Form(...),
    created_by: str = Form(...),
    image_file: UploadFile = File(...)
):
    """
    Uploads a face image, extracts the embedding, and stores them in SQL Server.
    """
    try:
        image_path = save_face_image(employee_id, image_file, created_by)
        embedding = extract_face_embedding(image_path)
        embedding_str = ",".join(map(str, embedding))
        modified_by = created_by

        query = "{CALL SaveOrUpdateFaceImage(?, ?, ?, ?, ?, ?, ?, ?)}"
        params = (employee_id, embedding_str, image_path, created_by, modified_by, None, None, None)
        result = execute_query_with_output(query, params)

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save face: {str(e)}")


# ✅ API to Verify Face
@router.post("/verify-face")
async def verify_face(image_file: UploadFile = File(...)):
    """
    Verifies a face by comparing it against stored faces.
    """
    try:
        # Save Temp Image for Verification
        temp_image_path = os.path.join(IMAGE_FOLDER, "temp.jpg")
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

        # Fetch All Stored Faces
        query = "SELECT EmployeeID, ImagePath FROM EmployeeFaces where IsActive=1 and IsDeleted = 0"
        face_db = fetch_all(query)

        if not face_db:
            raise HTTPException(status_code=404, detail="No face data found")

        # Compare with Stored Faces
        for store_employee_id, stored_image_path in face_db:
            result = DeepFace.verify(img1_path=temp_image_path, img2_path=stored_image_path, model_name="Facenet")

            if result["verified"]:
                return { "code":"00","employee_id": store_employee_id, "message": "Face Matched"}

        return {"code":"01","message": "No Match Found"}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during face verification: {str(e)}")

@router.post("/check-liveness/")
async def check_liveness_endpoint(file: UploadFile = File(...)):
    try:
        # Read image bytes
        image_bytes = await file.read()

        # Convert to NumPy array
        nparr = np.frombuffer(image_bytes, np.uint8)

        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Call the liveness detection function
        result = check_liveness(image)

        return result

    except Exception as e:
        return {"error": str(e)}
