import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState({
    total_jobs: 0,
    total_companies: 0,
    total_locations: 0,
    total_skills: 0
  })
  const [topSkills, setTopSkills] = useState([])
  const [distribution, setDistribution] = useState({})
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchDashboardData()
  }, [])
  
  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch all dashboard data
      const [statsRes, skillsRes, distRes] = await Promise.all([
        axios.get('/api/dashboard/stats'),
        axios.get('/api/dashboard/top-skills'),
        axios.get('/api/dashboard/job-distribution')
      ])
      
      setStats(statsRes.data)
      setTopSkills(skillsRes.data.skills?.slice(0, 20) || [])
      setDistribution(distRes.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']
  
  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }
  
  return (
    <div className="dashboard">
      <h1>Dashboard Overview</h1>
      
      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon jobs">📊</div>
          <div className="stat-info">
            <h3>{stats.total_jobs.toLocaleString()}</h3>
            <p>Total Job Postings</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon companies">🏢</div>
          <div className="stat-info">
            <h3>{stats.total_companies.toLocaleString()}</h3>
            <p>Companies</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon locations">📍</div>
          <div className="stat-info">
            <h3>{stats.total_locations.toLocaleString()}</h3>
            <p>Locations</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon skills">💼</div>
          <div className="stat-info">
            <h3>{stats.total_skills.toLocaleString()}</h3>
            <p>Trending Skills</p>
          </div>
        </div>
      </div>
      
      {/* Top Skills Chart */}
      <div className="chart-section">
        <h2>Top 20 In-Demand Skills</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={topSkills}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Skill" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Count" fill="#0088FE" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Job Type Distribution */}
      {distribution.job_types && distribution.job_types.length > 0 && (
        <div className="chart-section">
          <h2>
            {distribution.job_type_source === 'nlp_category'
              ? 'NLP Job Category Distribution'
              : 'Job Type Distribution'}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={distribution.job_types}
                dataKey="count"
                nameKey="type"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {distribution.job_types.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
      
      {/* Top Companies */}
      {distribution.top_companies && distribution.top_companies.length > 0 && (
        <div className="chart-section">
          <h2>Top 15 Hiring Companies</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={distribution.top_companies} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="company" type="category" width={150} />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#00C49F" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default Dashboard
