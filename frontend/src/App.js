import React, { useState } from 'react';
import '@/App.css';
import axios from 'axios';
import { Upload, Loader2, Info, MapPin, Beef, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }

    setSelectedImage(file);
    setResult(null);
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const analyzeBreed = async () => {
    if (!selectedImage) {
      toast.error('Please select an image first');
      return;
    }

    setIsScanning(true);
    setResult(null);

    try {
      const reader = new FileReader();
      reader.readAsDataURL(selectedImage);
      
      reader.onload = async () => {
        const base64String = reader.result.split(',')[1];
        
        const response = await axios.post(`${API}/recognize-breed`, {
          image_base64: base64String
        });

        if (response.data.success) {
          setResult(response.data);
          toast.success('Breed identified successfully!');
        } else {
          toast.error(response.data.error || 'Failed to identify breed');
        }
      };
    } catch (error) {
      console.error('Error analyzing breed:', error);
      toast.error('Failed to analyze image. Please try again.');
    } finally {
      setIsScanning(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setResult(null);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="header-nav">
        <div className="container-wrapper">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="logo-icon">
                <Beef className="w-6 h-6" />
              </div>
              <h1 className="logo-text">Breed Scanner</h1>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="text-stone-600 hover:text-primary"
              data-testid="info-button"
            >
              <Info className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-overlay" />
        <div className="container-wrapper hero-content">
          <div className="text-center mb-8">
            <h2 className="hero-title">
              AI-Powered Breed Recognition
            </h2>
            <p className="hero-subtitle">
              Upload an image of cattle or buffalo to identify the breed instantly
            </p>
          </div>

          {/* Upload Zone */}
          {!imagePreview ? (
            <div
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('fileInput').click()}
              data-testid="upload-zone"
            >
              <input
                id="fileInput"
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="hidden"
                data-testid="file-input"
              />
              <div className="upload-icon">
                <Upload className="w-16 h-16" />
              </div>
              <h3 className="upload-title">Upload Animal Image</h3>
              <p className="upload-description">
                Drag and drop or click to select
              </p>
              <p className="upload-hint">
                Supports JPG, PNG, WEBP formats
              </p>
            </div>
          ) : (
            <div className="preview-container">
              <Card className="preview-card">
                <div className="preview-image-wrapper">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="preview-image"
                    data-testid="preview-image"
                  />
                  {isScanning && (
                    <div className="scanning-overlay">
                      <div className="scan-line" />
                    </div>
                  )}
                </div>
                <div className="preview-actions">
                  <Button
                    onClick={analyzeBreed}
                    disabled={isScanning}
                    className="scan-button"
                    data-testid="analyze-button"
                  >
                    {isScanning ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5 mr-2" />
                        Identify Breed
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={resetAnalysis}
                    variant="outline"
                    disabled={isScanning}
                    className="reset-button"
                    data-testid="reset-button"
                  >
                    Upload New Image
                  </Button>
                </div>
              </Card>
            </div>
          )}
        </div>
      </section>

      {/* Results Section */}
      {result && result.success && (
        <section className="results-section">
          <div className="container-wrapper">
            <div className="results-grid">
              {/* Breed Card */}
              <Card className="breed-card" data-testid="breed-result-card">
                <div className="breed-header">
                  <h3 className="breed-name" data-testid="breed-name">{result.breed}</h3>
                  <div className="confidence-badge" data-testid="confidence-badge">
                    {result.confidence} Confidence
                  </div>
                </div>
                <div className="breed-type" data-testid="animal-type">
                  {result.animal_type === 'cattle' ? 'Cattle' : 'Buffalo'}
                </div>
              </Card>

              {/* Breed Details */}
              {result.breed_info && (
                <Card className="details-card" data-testid="breed-details-card">
                  <h4 className="details-title">Breed Information</h4>
                  <div className="details-grid">
                    <div className="detail-item">
                      <MapPin className="detail-icon" />
                      <div>
                        <p className="detail-label">Origin</p>
                        <p className="detail-value" data-testid="breed-origin">{result.breed_info.origin}</p>
                      </div>
                    </div>
                    <div className="detail-item">
                      <Info className="detail-icon" />
                      <div>
                        <p className="detail-label">Utility</p>
                        <p className="detail-value" data-testid="breed-utility">{result.breed_info.utility}</p>
                      </div>
                    </div>
                    <div className="detail-item">
                      <Sparkles className="detail-icon" />
                      <div>
                        <p className="detail-label">Key Traits</p>
                        <p className="detail-value" data-testid="breed-traits">{result.breed_info.traits}</p>
                      </div>
                    </div>
                    <div className="detail-item">
                      <div className="color-swatch" style={{backgroundColor: getColorCode(result.breed_info.color)}} />
                      <div>
                        <p className="detail-label">Color</p>
                        <p className="detail-value" data-testid="breed-color">{result.breed_info.color}</p>
                      </div>
                    </div>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="container-wrapper">
          <p className="footer-text">
            Powered by Gemini AI • Designed for Field Level Workers
          </p>
        </div>
      </footer>
    </div>
  );
}

// Helper function to get color code for visual representation
function getColorCode(colorName) {
  const colorMap = {
    'red': '#DC2626',
    'white': '#F3F4F6',
    'black': '#1F2937',
    'grey': '#9CA3AF',
    'brown': '#92400E',
    'copper': '#B45309'
  };
  
  const lowerColor = colorName.toLowerCase();
  for (const [key, value] of Object.entries(colorMap)) {
    if (lowerColor.includes(key)) {
      return value;
    }
  }
  return '#6B7280';
}

export default App;
