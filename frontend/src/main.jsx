import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.jsx'
import './index.css'

// Configure API base URL from environment
// If VITE_API_BASE_URL is set (in production), use it; otherwise use proxy (local dev)
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || ''

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
