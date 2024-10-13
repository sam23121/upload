from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class ImageBase(BaseModel):
    filename: str
    url: str
    description: Optional[str] = None
    upload_date: datetime

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
