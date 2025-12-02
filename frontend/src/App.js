import React, { useState } from 'react';
import '@/App.css';
import axios from 'axios';
import { Upload, Loader2, Info, MapPin, Beef, Sparkles, Award, Eye } from 'lucide-react';
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
              <h1 className="logo-text">CattleLens</h1>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium" style={{ color: '#8B4513' }}>Powered by VinayKarthik</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-overlay" />
        <div className="container-wrapper hero-content">
          <div className="text-center mb-8">
            <h2 className="hero-title">
              Indian Cattle & Buffalo Breed Identification
            </h2>
            <p className="hero-subtitle">
              Advanced AI-powered breed recognition for Indian livestock breeds. Upload an image to identify cattle or buffalo breeds with detailed information.
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
            {/* Image Quality Banner */}
            {result.image_quality && (
              <div className="image-quality-banner">
                <Eye className="inline-block w-5 h-5 mr-2" />
                Image Quality: {result.image_quality}
              </div>
            )}

            <div className="results-grid">
              {/* Breed Card */}
              <Card className="breed-card" data-testid="breed-result-card">
                <div className="breed-header">
                  <h3 className="breed-name" data-testid="breed-name">{result.breed}</h3>
                  <div className="confidence-badge" data-testid="confidence-badge">
                    <Award className="inline-block w-4 h-4 mr-1" />
                    {result.confidence} Confidence
                  </div>
                </div>
                <div className="breed-type" data-testid="animal-type">
                  {result.animal_type === 'cattle' ? 'Cattle Breed' : 'Buffalo Breed'}
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
                      <div className="color-swatch" style={{ backgroundColor: getColorCode(result.breed_info.color) }} />
                      <div>
                        <p className="detail-label">Color</p>
                        <p className="detail-value" data-testid="breed-color">{result.breed_info.color}</p>
                      </div>
                    </div>
                    {result.breed_info.horn_shape && (
                      <div className="detail-item">
                        <Award className="detail-icon" />
                        <div>
                          <p className="detail-label">Horn Shape</p>
                          <p className="detail-value">{result.breed_info.horn_shape}</p>
                        </div>
                      </div>
                    )}
                    {result.breed_info.size && (
                      <div className="detail-item">
                        <Info className="detail-icon" />
                        <div>
                          <p className="detail-label">Size</p>
                          <p className="detail-value">{result.breed_info.size}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </Card>
              )}
            </div>

            {/* Alternative Breeds Section */}
            {result.alternative_breeds && result.alternative_breeds.length > 0 && (
              <div className="alternatives-section">
                <h3 className="alternatives-title">Alternative Breed Possibilities</h3>
                <div className="alternatives-grid">
                  {result.alternative_breeds.map((alt, index) => (
                    <Card key={index} className="alternative-card">
                      <h4 className="alternative-breed-name">{alt.breed}</h4>
                      <span className="alternative-confidence">{alt.confidence}</span>
                      <p className="alternative-reasoning">{alt.reasoning}</p>
                      {alt.breed_info && (
                        <div className="text-sm" style={{ color: '#8D6E63' }}>
                          <p><strong>Origin:</strong> {alt.breed_info.origin}</p>
                          <p><strong>Utility:</strong> {alt.breed_info.utility}</p>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="container-wrapper">
          <p className="footer-text">
            Powered by VinayKarthik • Supporting Indian Livestock Conservation
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
    'gray': '#9CA3AF',
    'brown': '#92400E',
    'copper': '#B45309',
    'silver': '#C0C0C0',
    'reddish': '#DC2626',
    'dun': '#C19A6B',
    'rusty': '#B7410E'
  };

  const lowerColor = colorName.toLowerCase();
  for (const [key, value] of Object.entries(colorMap)) {
    if (lowerColor.includes(key)) {
      return value;
    }
  }
  return '#8D6E63';
}

export default App;
