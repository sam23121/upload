# Image Upload and Analysis App

## Overview

This application is a web-based platform that allows users to securely upload and manage images. It features user authentication, integration with Amazon S3 for image storage, and uses OpenAI's API to generate descriptions for uploaded images.

## Features

- User registration and authentication
- Secure image upload to Amazon S3
- Automatic image description generation using OpenAI's API
- Image gallery with descriptions and upload dates
- Responsive web interface

## Tech Stack

### Frontend
- React with TypeScript
- Vite for build tooling
- Axios for API requests
- React Router for navigation

### Backend
- Python FastAPI
- SQLAlchemy for database ORM
- PostgreSQL as the database
- Boto3 for AWS S3 integration
- OpenAI API for image description generation

## Setup

### Prerequisites
- Node.js and npm
- Python 3.7+
- PostgreSQL database
- AWS S3 bucket
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:   ```
   cd backend   ```

2. Create a virtual environment:   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`   ```

3. Install dependencies:   ```
   pip install -r requirements.txt   ```

4. Set up environment variables:
   Create a `.env` file in the backend directory with the following content:   ```
   DATABASE_URL=your_postgresql_connection_string
   SECRET_KEY=your_secret_key
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   S3_BUCKET_NAME=your_s3_bucket_name
   OPENAI_API_KEY=your_openai_api_key   ```

5. Run the backend server:   ```
   uvicorn app.main:app --reload   ```

### Frontend Setup

1. Navigate to the frontend directory:   ```
   cd frontend   ```

2. Install dependencies:   ```
   npm install   ```

3. Start the development server:   ```
   npm run dev   ```

## Usage

1. Register a new account or log in to an existing one.
2. On the dashboard, you can upload new images.
3. View your uploaded images along with their AI-generated descriptions.

## API Endpoints

- `POST /register`: Register a new user
- `POST /token`: Login and receive an access token
- `POST /upload-image`: Upload a new image
- `GET /images`: Retrieve all images for the current user




