import React from 'react'
import { Link, useLocation, Outlet, useNavigate } from 'react-router-dom'
import { FiHome, FiUpload, FiBarChart2, FiDownload, FiUser, FiLogOut } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'
import './Layout.css'

function Layout() {
  const location = useLocation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  
  const navItems = [
    { path: '/home', label: 'Home', icon: FiHome },
    { path: '/dashboard', label: 'Dashboards', icon: FiBarChart2 },
    { path: '/upload', label: 'Upload', icon: FiUpload },
    { path: '/download', label: 'Download', icon: FiDownload }
  ]

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }
  
  return (
    <div className="layout">
      <aside className="sidebar">
        <Link to="/" className="logo">
          <h1>Job Skills NLP</h1>
          <p>Analysis Platform</p>
        </Link>
        
        <nav className="nav">
          {navItems.map(item => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon className="nav-icon" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="user-section">
          {user ? (
            <>
              <div className="user-info">
                <FiUser className="user-avatar" />
                <div className="user-details">
                  <div className="user-name">{user.username}</div>
                  <div className="user-email">{user.email}</div>
                </div>
              </div>
              <button onClick={handleLogout} className="logout-btn">
                <FiLogOut /> Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="login-link">
              <FiUser /> Sign In
            </Link>
          )}
        </div>
      </aside>
      
      <main className="main-content">
        <header className="header">
          <h1>Job Skills NLP Analysis</h1>
        </header>
        
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
