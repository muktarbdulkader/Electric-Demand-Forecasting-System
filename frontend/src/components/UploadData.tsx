import React, { useState, useRef } from "react";
import { uploadData, UploadResponse } from "../services/api";

const UploadData: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadData(file);
      setResult(response);
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to upload file. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="upload-card">
      <h3>📤 Upload Real Data</h3>
      <p>Upload CSV file to retrain the ML model with your data</p>
      <p style={{ fontSize: "12px", color: "#64748b", marginTop: "8px" }}>
        Required column: <strong>demand</strong> (MW)<br/>
        Optional: datetime, temperature, hour, day_of_week, month, humidity, is_holiday, region
      </p>
      
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleUpload}
        accept=".csv"
        style={{ display: "none" }}
      />
      
      <button 
        className="upload-btn" 
        onClick={triggerUpload}
        disabled={uploading}
      >
        {uploading ? "⏳ Uploading & Training..." : "📁 Select CSV File"}
      </button>

      {result && (
        <div className="upload-success">
          <strong>✅ Success!</strong><br/>
          {result.message}<br/>
          <small>Records processed: {result.records_processed}</small>
        </div>
      )}

      {error && (
        <div className="upload-error">
          <strong>❌ Error</strong><br/>
          {error}
        </div>
      )}
    </div>
  );
};

export default UploadData;
