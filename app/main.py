from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routes import face_recognition

app = FastAPI(
    title="Smart Employee Portal — Face Recognition API",
    description="Face enrolment, verification and liveness checks for attendance, built with DeepFace, OpenCV and a FAISS index.",
    version="1.0.0",
)

# Include API routes
app.include_router(face_recognition.router)

@app.get("/", include_in_schema=False)
def home():
    """ Redirect root URL to Swagger UI """
    return RedirectResponse(url="/docs")


