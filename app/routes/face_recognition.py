import os
import shutil
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.services.database import execute_query, fetch_all
from deepface import DeepFace

# Define the storage directory
IMAGE_FOLDER = "images/faces/"

# Ensure the folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

router = APIRouter(prefix="/face-recognition", tags=["Face Recognition"])


# ✅ Function to Save Image
def save_face_image(user_id: int, image_file: UploadFile) -> str:
    """Saves an uploaded face image to 'images/faces/user_{user_id}/' and returns its path."""
    user_folder = os.path.join(IMAGE_FOLDER, f"user_{user_id}")
    os.makedirs(user_folder, exist_ok=True)  # Create folder if not exists

    image_path = os.path.join(user_folder, image_file.filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    return image_path


# ✅ Function to Extract Face Embedding
def extract_face_embedding(image_path: str) -> list:
    """Extracts face embedding using DeepFace and returns it as a list."""
    try:
        embedding = DeepFace.represent(img_path=image_path, model_name="Facenet")[0]["embedding"]
        return embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting face embedding: {str(e)}")


# ✅ API to Save Face Image & Embedding
@router.post("/save-face")
async def save_face(
    user_id: int = Form(...),
    created_by: str = Form(...),
    image_file: UploadFile = File(...)
):
    """
    Uploads a face image, extracts the embedding, and stores them in SQL Server.
    """
    try:
        # Save Image
        image_path = save_face_image(user_id, image_file)

        # Extract Embedding
        embedding = extract_face_embedding(image_path)
        embedding_str = json.dumps(embedding)

        # Save to Database (Including CreatedBy )
        query = """
        INSERT INTO UserFaces (UserID, Embedding, ImagePath, CreatedBy,)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (user_id, embedding_str, image_path, created_by)

        execute_query(query, params)

        return {"code":"00","message": "Face saved successfully", "image_path": image_path}

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
        query = "SELECT UserID, ImagePath FROM UserFaces"
        face_db = fetch_all(query)

        if not face_db:
            raise HTTPException(status_code=404, detail="No face data found")

        # Compare with Stored Faces
        for stored_user_id, stored_image_path in face_db:
            result = DeepFace.verify(img1_path=temp_image_path, img2_path=stored_image_path, model_name="Facenet")

            if result["verified"]:
                return { "code":"00","user_id": stored_user_id, "message": "Face Matched"}

        return {"code":"01","message": "No Match Found"}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during face verification: {str(e)}")
