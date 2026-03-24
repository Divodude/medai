import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, ImageIcon, Loader2, MapPin } from 'lucide-react';
import useHealthStore from '../store/useHealthStore';
import { analyzeReport } from '../api/client';
import { v4 as uuidv4 } from 'uuid';

function getLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve({});
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude: lat, longitude: lng } = pos.coords;
        let city = '';
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`
          );
          const data = await res.json();
          city =
            data.address?.city ||
            data.address?.town ||
            data.address?.village ||
            data.address?.county ||
            '';
        } catch (_) { }
        resolve({ lat, lng, city });
      },
      () => resolve({})
    );
  });
}

export default function UploadZone() {
  const { setAnalysisResult, setIsAnalyzing, isAnalyzing, sessionId, setSessionId, patientName, setUserLocation } =
    useHealthStore();
  const [preview, setPreview] = useState(null);
  const [locText, setLocText] = useState('');
  const [error, setError] = useState('');

  const onDrop = useCallback(
    async (accepted) => {
      if (!accepted.length) return;
      const file = accepted[0];
      setPreview(URL.createObjectURL(file));
      setError('');
      setIsAnalyzing(true);

      try {
        const location = await getLocation();
        if (location.city) {
          setLocText(`📍 ${location.city}`);
          setUserLocation(location.city);
        }

        let sid = sessionId;
        if (!sid) {
          sid = uuidv4();
          setSessionId(sid);
        }

        const result = await analyzeReport({
          file,
          sessionId: sid,
          lat: location.lat,
          lng: location.lng,
          city: location.city,
          patientName,
        });

        setAnalysisResult(result);
      } catch (err) {
        setError('Analysis failed. Please check the backend is running.');
        console.error(err);
      } finally {
        setIsAnalyzing(false);
      }
    },
    [sessionId, patientName, setAnalysisResult, setIsAnalyzing, setSessionId]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': [] },
    multiple: false,
    disabled: isAnalyzing,
  });

  return (
    <div className="upload-section">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'dropzone--active' : ''} ${isAnalyzing ? 'dropzone--loading' : ''}`}
      >
        <input {...getInputProps()} />

        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Report preview" className="preview-img" />
            <div className="preview-overlay">
              {isAnalyzing ? (
                <div className="analyzing-badge">
                  <Loader2 size={18} className="spin" />
                  Analyzing with AI…
                </div>
              ) : (
                <div className="analyzing-badge analyzing-badge--done">
                  ✓ Analysis Complete — Drop another to re-analyze
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="dropzone-idle">
            <div className="dropzone-icon-wrap">
              {isDragActive ? <ImageIcon size={40} /> : <Upload size={40} />}
            </div>
            <h2 className="dropzone-title">
              {isDragActive ? 'Release to analyze' : 'Drop your medical report here'}
            </h2>
            <p className="dropzone-sub">Supports JPG, PNG, PDF screenshots · Powered by Llama 4 Scout</p>
          </div>
        )}
      </div>

      {locText && (
        <div className="loc-tag">
          <MapPin size={13} /> {locText}
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}
    </div>
  );
}
