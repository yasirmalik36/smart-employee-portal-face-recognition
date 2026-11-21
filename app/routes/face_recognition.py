import os
import shutil
import tempfile
import uuid
import numpy as np
import cv2
import faiss
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from deepface import DeepFace
from app.services.database import execute_query_with_output, fetch_all, delete_record
from app.services.liveness import check_liveness

# Define the storage directory
IMAGE_FOLDER = "images/faces/"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Initialize ArcFace model
model = DeepFace.build_model("ArcFace")

# Initialize FAISS Index
embedding_dim = 512  # ArcFace output dimension
faiss_index = faiss.IndexFlatL2(embedding_dim)
embeddings_dict = {}  # Mapping FAISS index → employee_id

router = APIRouter(prefix="/face-recognition", tags=["Face Recognition"])

# Load existing embeddings
def load_existing_embeddings():
    global faiss_index, embeddings_dict
    faiss_index = faiss.IndexFlatL2(embedding_dim)  # Reset FAISS
    embeddings_dict.clear()  # Clear existing mappings

    query = "SELECT EmployeeID, Embedding FROM EmployeeFaces WHERE IsActive=1 AND IsDeleted=0"
    face_db = fetch_all(query)

    if not face_db:
        print("ℹ️ No stored face data found in the database.")
        return

    embeddings = []
    employee_ids = []

    for employee_id, embedding_str in face_db:
        embedding = np.array([float(x) for x in embedding_str.split(',')], dtype=np.float32)
        embedding /= np.linalg.norm(embedding)  # Normalize embedding
        embeddings.append(embedding)
        employee_ids.append(employee_id)

    if embeddings:
        faiss_index.add(np.array(embeddings, dtype=np.float32))  # Add all at once
        for idx, emp_id in enumerate(employee_ids):
            embeddings_dict[idx] = emp_id

    print(f"✅ Loaded {faiss_index.ntotal} embeddings into FAISS.")

# Load embeddings on startup
load_existing_embeddings()

# Extract face embedding from an image
def extract_face_embedding(image_path: str) -> np.ndarray:
    try:
        print(f"[INFO] Extracting face embedding from: {image_path}")
        embedding = DeepFace.represent(img_path=image_path, model_name="ArcFace")[0]["embedding"]
        embedding = np.array(embedding, dtype=np.float32)
        return embedding / np.linalg.norm(embedding)  # Normalize the embedding
    except Exception as e:
        print(f"[ERROR] Face embedding extraction failed: {str(e)}")
        return None

# Save face image to the specified folder
def save_face_image(employee_id: int, image_file: UploadFile) -> str:
    employee_folder = os.path.join(IMAGE_FOLDER, f"employee_{employee_id}")
    os.makedirs(employee_folder, exist_ok=True)
    # Never trust the client-supplied filename (path traversal like "../../x"); generate our own.
    ext = os.path.splitext(image_file.filename or "")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
        ext = ".jpg"
    image_path = os.path.join(employee_folder, f"{uuid.uuid4().hex}{ext}")
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)
    return image_path

# Save face image and embedding to the database and FAISS index
@router.post("/save-face")
async def save_face(employee_id: int = Form(...), created_by: str = Form(...), image_file: UploadFile = File(...)):
    try:
        image_path = save_face_image(employee_id, image_file)
        embedding = extract_face_embedding(image_path)

        if embedding is None:
            return {"code": "02", "message": "Failure", "description": "No face detected in the uploaded image. Please upload a clear face photo."}

        faiss_index.add(np.array([embedding], dtype=np.float32))
        index_position = faiss_index.ntotal - 1
        embeddings_dict[index_position] = employee_id

        embedding_str = ",".join(map(str, embedding.tolist()))
        query = "{CALL SaveOrUpdateFaceImage(?, ?, ?, ?, ?, ?, ?, ?)}"
        params = (employee_id, embedding_str, image_path, created_by, created_by, None, None, None)
        result = execute_query_with_output(query, params)
        load_existing_embeddings()

        return result
    except Exception as e:
        return {"code": "500", "message": "Failure", "description": f"Failed to save face: {str(e)}"}

# Verify face by matching the uploaded image with existing database
@router.post("/verify-face")
async def verify_face(image_file: UploadFile = File(...)):
    # A unique temp file per request. A single shared "temp.jpg" let two simultaneous
    # requests overwrite each other's image, so one person could be matched as another.
    fd, temp_image_path = tempfile.mkstemp(suffix=".jpg")
    try:
        with os.fdopen(fd, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

        # Extract face embedding
        embedding = extract_face_embedding(temp_image_path)
        if embedding is None:
            return {"code": "02", "message": "Failure", "description": "Face not recognized. Please try again later"}

        if faiss_index.ntotal > 0:
            # Convert embedding to numpy array
            embedding_array = np.array([embedding], dtype=np.float32)

            # FAISS search
            D, I = faiss_index.search(embedding_array, 1)

            if D[0][0] < 1.2:
                matched_index = I[0][0]
                employee_id = embeddings_dict.get(matched_index)
                if employee_id is not None:
                    return {
                        "code": "00",
                        "message": "Success",
                        "employee_id": employee_id,
                        "description": "Face Matched (FAISS)"
                    }

        # Fetch stored employee faces from DB
        query = "SELECT EmployeeID, ImagePath FROM EmployeeFaces WHERE IsActive=1 AND IsDeleted=0"
        face_db = fetch_all(query)

        if not face_db:
            return {"code": "03", "message": "Failure", "description": "No face data found in the database"}

        # Verify face with DeepFace
        for store_employee_id, stored_image_path in face_db:
            try:
                result = DeepFace.verify(img1_path=temp_image_path, img2_path=stored_image_path, model_name="Facenet")
                if result.get("verified"):
                    return {
                        "code": "00",
                        "message": "Success",
                        "employee_id": store_employee_id,
                        "description": "Face Matched (DeepFace)"
                    }
            except Exception as deepface_error:
                print(f"DeepFace error: {deepface_error}")

        return {"code": "01", "message": "Failure", "description": "No Match Found"}

    except Exception as e:
        return {"code": "500", "message": "Failure", "description": f"Error during face verification: {str(e)}"}
    finally:
        try:
            os.remove(temp_image_path)
        except OSError:
            pass

# Check liveness to verify the person is real.
# The .NET backend calls "/check-liveness" (no trailing slash); the old route only matched
# "/check-liveness/", which caused a redirect that drops the uploaded file. Accept both.
@router.post("/check-liveness")
@router.post("/check-liveness/", include_in_schema=False)
async def check_liveness_endpoint(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        result = check_liveness(image)
        return result
    except Exception as e:
        return {"error": str(e)}

# Delete face data from database and filesystem
@router.delete("/delete-face/{employee_id}")
async def delete_face(employee_id: int):
    try:
        query = "SELECT FaceID, ImagePath FROM EmployeeFaces WHERE EmployeeID=? AND IsDeleted=0 AND IsActive=1"
        result = fetch_all(query, (employee_id,))

        if not result:
            return {"code": "404", "message": "Failure", "description": "Face not found for the given Employee ID"}

        delete_record("EmployeeFaces", "EmployeeID=? AND IsDeleted=0 AND IsActive=1", (employee_id,))

        # The DELETE removes every matching row, so remove every matching image too
        # (previously only the first one was deleted and the rest stayed on disk).
        for _face_id, image_path in result:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                employee_folder = os.path.dirname(image_path)
                if os.path.exists(employee_folder) and not os.listdir(employee_folder):
                    os.rmdir(employee_folder)
        load_existing_embeddings()

        return {"code": "00", "message": "Success", "description": "Face deleted successfully"}

    except Exception as e:
        return {"code": "500", "message": "Failure", "description": f"Error deleting face: {str(e)}"}
