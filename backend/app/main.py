# Inside main.py
import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.database import get_db, init_db
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, File
import uuid
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from openai import OpenAI
from PIL import Image
import io




load_dotenv()

app = FastAPI()

# Add this after creating the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT token functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# User registration
@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    # print(db_user)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # print(db_user)
    return db_user

# User login
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route example
@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# TODO: Implement image upload, retrieval, and AI analysis endpoints

# S3 setup
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='eu-north-1'
    
)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# S3 helper functions
def upload_file_to_s3(file: UploadFile, object_name: str):
    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_name)
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return False
    return True

def generate_presigned_url(object_name: str, expiration=3600):
    # print(object_name)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': S3_BUCKET_NAME,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None
    return response


# Add this after the S3 setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Add this function to generate image description
def generate_image_description(image_url: str) -> str:
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": "Give me a short description of this image"},
                {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating image description: {e}")
        return "No description available"

# Modify the upload_image function
@app.post("/upload-image", response_model=schemas.Image)
async def upload_image(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(f"Received file: {file.filename}")
    # Generate a unique filename
    file_extension = file.filename.split(".")[-1]
    object_name = f"{uuid.uuid4()}.{file_extension}"
    
    # Upload the file to S3
    if not upload_file_to_s3(file, object_name):
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")
    
    # Generate a presigned URL for the uploaded image
    url = generate_presigned_url(object_name)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")
    
    # Generate image description using OpenAI
    description = generate_image_description(url)
    
    # Create a new image record in the database
    new_image = models.Image(
        filename=file.filename, 
        url=url, 
        description=description, 
        owner_id=current_user.id,
        upload_date=datetime.utcnow()  # Add this line
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    return new_image

# Add this after the upload_image endpoint

@app.get("/images", response_model=List[schemas.Image])
async def get_images(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    images = db.query(models.Image).filter(models.Image.owner_id == current_user.id).order_by(models.Image.upload_date.desc()).all()
    
    return images

@app.on_event("startup")
async def startup_event():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
