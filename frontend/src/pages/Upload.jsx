import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { FiUpload, FiFile, FiCheckCircle, FiXCircle, FiClock } from 'react-icons/fi'
import './Upload.css'

function Upload() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadHistory, setUploadHistory] = useState([])
  const [message, setMessage] = useState({ type: '', text: '' })
  
  useEffect(() => {
    fetchUploadHistory()
  }, [])
  
  const fetchUploadHistory = async () => {
    try {
      const response = await axios.get('/api/upload/history')
      setUploadHistory(response.data.uploads || [])
    } catch (error) {
      console.error('Error fetching upload history:', error)
    }
  }
  
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // Validate file type
      const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/pdf']
      if (validTypes.includes(selectedFile.type) || selectedFile.name.endsWith('.csv') || selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.pdf')) {
        setFile(selectedFile)
        setMessage({ type: '', text: '' })
      } else {
        setMessage({ type: 'error', text: 'Invalid file type. Please upload CSV, Excel, or PDF files only.' })
        setFile(null)
      }
    }
  }
  
  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'Please select a file first.' })
      return
    }
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      setUploading(true)
      setMessage({ type: '', text: '' })
      
      const response = await axios.post('/api/upload/file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setMessage({ type: 'success', text: `File uploaded successfully! Processing started.` })
      setFile(null)
      
      // Refresh upload history
      setTimeout(() => {
        fetchUploadHistory()
      }, 1000)
      
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Upload failed. Please try again.' 
      })
    } finally {
      setUploading(false)
    }
  }
  
  const handleDragOver = (e) => {
    e.preventDefault()
  }
  
  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileChange({ target: { files: [droppedFile] } })
    }
  }
  
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <FiCheckCircle className="status-icon success" />
      case 'failed':
        return <FiXCircle className="status-icon error" />
      case 'processing':
        return <FiClock className="status-icon processing" />
      default:
        return <FiClock className="status-icon pending" />
    }
  }
  
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }
  
  return (
    <div className="upload-page">
      <h1>Upload New Data</h1>
      <p className="subtitle">Upload job posting data (CSV, Excel, or PDF) to retrain the model and update analysis</p>
      
      {/* Upload Section */}
      <div 
        className="upload-section"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <div className="upload-box">
          <FiUpload className="upload-icon" />
          <h3>Drag & Drop your file here</h3>
          <p>or</p>
          <label htmlFor="file-input" className="file-input-label">
            Browse Files
          </label>
          <input
            id="file-input"
            type="file"
            accept=".csv,.xlsx,.pdf"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <p className="file-info">Supported formats: CSV, XLSX, PDF (Max 500MB)</p>
        </div>
        
        {file && (
          <div className="selected-file">
            <FiFile className="file-icon" />
            <div className="file-details">
              <p className="file-name">{file.name}</p>
              <p className="file-size">{formatFileSize(file.size)}</p>
            </div>
            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
          </div>
        )}
        
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
      </div>
      
      {/* Upload History */}
      <div className="history-section">
        <h2>Upload History</h2>
        {uploadHistory.length === 0 ? (
          <p className="no-data">No upload history yet.</p>
        ) : (
          <div className="history-table">
            <table>
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Filename</th>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Records</th>
                  <th>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {uploadHistory.map(upload => (
                  <tr key={upload.id}>
                    <td>{getStatusIcon(upload.status)}</td>
                    <td>{upload.filename}</td>
                    <td>{upload.file_type?.toUpperCase()}</td>
                    <td>{formatFileSize(upload.file_size)}</td>
                    <td>{upload.records_processed || '-'}</td>
                    <td>{new Date(upload.uploaded_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default Upload
