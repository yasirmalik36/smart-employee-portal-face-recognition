 
**Face Recognition API with FastAPI**

This project is a Face Recognition System built with FastAPI, integrating DeepFace for face verification and SQL Server for storing user face embeddings.

🚀 Features

✅ Upload and save face images

✅ Extract face embeddings using DeepFace (Facenet model)

✅ Store user face data in SQL Server

✅ Face verification against stored records

✅ FastAPI-based RESTful API

📌 Technologies Used

FastAPI - Web framework for building APIs

DeepFace - Face recognition and verification

SQL Server - Database for storing user face data

Uvicorn - ASGI server for FastAPI

📂 Project Structure

📦 smart-employee-portal-face-recognition
│-- 📁 models/              # Deep learning model files
│-- 📁 database/            # Database connection & queries
│-- 📁 routes/              # API endpoints
│-- 📁 static/              # Uploaded face images
│-- 📄 main.py              # FastAPI application entry point
│-- 📄 requirements.txt     # Python dependencies
│-- 📄 README.md            # Project documentation

⚙️ Installation & Setup

1️⃣ Clone the Repository

git clone https://github.com/your-repo-name.git
cd smart-employee-portal-face-recognition

2️⃣ Create a Virtual Environment

python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate     # On Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Configure Database

Ensure SQL Server is running.

Update the database connection settings in database/config.py.

5️⃣ Run the FastAPI Server

uvicorn main:app --reload

The API will be available at: http://127.0.0.1:8000

🔥 API Endpoints

➤ Upload & Save Face

POST /save-face

Parameters:

user_id: (int) User ID

user_name: (optional, string) Username

image_file: (file) Face image

Response:

{
  "message": "Face saved successfully",
  "image_path": "path/to/saved/image.jpg"
}

➤ Verify Face

POST /verify-face

Parameters:

image_file: (file) Face image to verify

Response:

{
  "user_id": 123,
  "status": "Face Matched"
}

🛠️ Troubleshooting

Issue: Cannot insert NULL into column 'CreatedDate'

Solution: Ensure CreatedDate has a default value or pass a valid date.

Issue: DeepFace model not found

Solution: Ensure facenet_weights.h5 is downloaded to .deepface/weights/.

📜 License

This project is licensed under the MIT License.





📞 Contact

Author: Your Name

Email: your.email@example.com

GitHub: your-repo-link