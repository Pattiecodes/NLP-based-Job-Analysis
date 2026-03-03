import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.jsx'
import './index.css'

// Configure API base URL from environment
// In local dev, fallback to Flask localhost if env var isn't set
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || (isLocalhost ? 'http://localhost:5000' : '')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
