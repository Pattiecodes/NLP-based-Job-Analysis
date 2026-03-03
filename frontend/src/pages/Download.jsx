import { useState, useEffect } from 'react';
import axios from 'axios';
import { FiDownload, FiFileText, FiDatabase } from 'react-icons/fi';
import './Download.css';

function Download() {
  const [stats, setStats] = useState(null);
  const [downloading, setDownloading] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (type) => {
    setDownloading(type);
    
    try {
      let url = '';
      let filename = '';
      
      switch(type) {
        case 'jobs':
          url = '/api/download/jobs';
          filename = 'job_postings.csv';
          break;
        case 'skills':
          url = '/api/download/skills';
          filename = 'top_skills.csv';
          break;
        case 'analysis':
          url = '/api/download/analysis';
          filename = 'analysis_results.csv';
          break;
        case 'clusters':
          url = '/api/download/clusters';
          filename = 'clusters.csv';
          break;
        case 'topics':
          url = '/api/download/topics';
          filename = 'topics.csv';
          break;
        default:
          return;
      }

      const response = await axios.get(url, {
        responseType: 'blob'
      });

      // Create download link
      const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Error downloading file:', error);
      alert('Failed to download file. Please try again.');
    } finally {
      setDownloading(null);
    }
  };

  const downloadOptions = [
    {
      id: 'jobs',
      title: 'Job Postings Data',
      description: 'Download all processed job postings with extracted information',
      icon: FiDatabase,
      count: stats?.total_jobs || 0
    },
    {
      id: 'skills',
      title: 'Trending Skills',
      description: 'Download the list of top trending skills with frequency counts',
      icon: FiFileText,
      count: stats?.total_skills || 0
    },
    {
      id: 'analysis',
      title: 'Complete Analysis Results',
      description: 'Download full analysis including clusters, topics, and TF-IDF scores',
      icon: FiFileText,
      count: 'Full'
    },
    {
      id: 'clusters',
      title: 'Job Clusters',
      description: 'Download clustering results with keywords and job assignments',
      icon: FiDatabase,
      count: '6'
    },
    {
      id: 'topics',
      title: 'Topic Modeling Results',
      description: 'Download LDA topic modeling results with keywords and weights',
      icon: FiFileText,
      count: '8'
    }
  ];

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="download-page">
      <div className="download-header">
        <h1>Download Analysis Data</h1>
        <p className="subtitle">
          Export any of the analyzed datasets to your local computer for further analysis or reporting
        </p>
      </div>

      <div className="download-grid">
        {downloadOptions.map((option) => {
          const Icon = option.icon;
          const isDownloading = downloading === option.id;
          
          return (
            <div key={option.id} className="download-card">
              <div className="download-card-icon">
                <Icon />
              </div>
              <div className="download-card-content">
                <h3>{option.title}</h3>
                <p>{option.description}</p>
                <div className="download-card-meta">
                  <span className="data-count">
                    {typeof option.count === 'number' ? `${option.count.toLocaleString()} records` : option.count}
                  </span>
                </div>
              </div>
              <button
                className="download-btn"
                onClick={() => handleDownload(option.id)}
                disabled={isDownloading}
              >
                {isDownloading ? (
                  <>
                    <span className="spinner"></span>
                    Downloading...
                  </>
                ) : (
                  <>
                    <FiDownload />
                    Download CSV
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      <div className="download-info">
        <h3>About the Data</h3>
        <ul>
          <li>All files are exported in CSV format for easy import into Excel, R, Python, or other analysis tools</li>
          <li>Job postings data includes cleaned text, extracted skills, and metadata</li>
          <li>Analysis results contain TF-IDF scores, cluster assignments, and topic distributions</li>
          <li>Data is based on {stats?.total_jobs?.toLocaleString() || 0} LinkedIn job postings</li>
        </ul>
      </div>
    </div>
  );
}

export default Download;
