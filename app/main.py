from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routes import face_recognition

app = FastAPI()

# Include API routes
app.include_router(face_recognition.router)

@app.get("/", include_in_schema=False)
def home():
    """ Redirect root URL to Swagger UI """
    return RedirectResponse(url="/docs")


