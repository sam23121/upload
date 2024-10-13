import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface Image {
  id: string;
  url: string;
  filename: string;
  description: string | null;
  upload_date: string;
}

const Dashboard: React.FC = () => {
  const [images, setImages] = useState<Image[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      const response = await axios.get<Image[]>(`${API_BASE_URL}/images`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setImages(response.data);
    } catch (error) {
      console.error('Failed to fetch images:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      await axios.post(`${API_BASE_URL}/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      fetchImages();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div>
      <h2>Dashboard</h2>
      <button onClick={handleLogout}>Logout</button>
      <div>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload Image</button>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
        {images.map((image) => (
          <div key={image.id} style={{ width: '200px', marginBottom: '20px' }}>
            <img 
              src={image.url} 
              alt={image.filename} 
              style={{ width: '100%', height: 'auto' }} 
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.onerror = null;
                target.src = 'https://via.placeholder.com/200?text=Image+Not+Found';
              }}
            />
            <p>{image.filename}</p>
            <p>{image.description || 'No description'}</p>
            <p>Uploaded: {new Date(image.upload_date).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
