
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User Model (For API Requests & Responses)
class User(BaseModel):
    user_id: Optional[int] = None
    username: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    role: str
    profile_image: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    ip_address: Optional[str] = None
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_by: Optional[str] = None
    modified_date: Optional[datetime] = None
    failed_login_attempts: int = 0
    lockout_end: Optional[datetime] = None

# Face Embedding Model
class UserFace(BaseModel):
    user_id: int
    embedding: str  # Stringified list of face embeddings
    image_path: str
