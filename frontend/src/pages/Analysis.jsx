import { useState, useEffect } from 'react';
import axios from 'axios';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import './Analysis.css';

function Analysis() {
  const [clusters, setClusters] = useState([]);
  const [topics, setTopics] = useState([]);
  const [jobDescription, setJobDescription] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  useEffect(() => {
    fetchAnalysisData();
  }, []);

  const fetchAnalysisData = async () => {
    try {
      const [clustersRes, topicsRes] = await Promise.all([
        axios.get('/api/dashboard/clusters'),
        axios.get('/api/dashboard/topics')
      ]);
      
      setClusters(clustersRes.data.clusters || []);
      setTopics(topicsRes.data.topics || []);
    } catch (error) {
      console.error('Error fetching analysis data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) return;
    
    setAnalyzing(true);
    setPrediction(null);
    
    try {
      const [clusterRes, topicRes, skillsRes] = await Promise.all([
        axios.post('/api/analysis/cluster/predict', { text: jobDescription }),
        axios.post('/api/analysis/topic/predict', { text: jobDescription }),
        axios.post('/api/analysis/skills/extract', { text: jobDescription })
      ]);
      
      setPrediction({
        cluster: clusterRes.data,
        topic: topicRes.data,
        skills: skillsRes.data
      });
    } catch (error) {
      console.error('Error analyzing job description:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading analysis data...</div>;
  }

  return (
    <div className="analysis-page">
      <h1>Job Market Analysis</h1>
      <p className="subtitle">Explore job clusters, topic distributions, and analyze job descriptions</p>

      <div className="analysis-grid">
        {/* Cluster Visualization */}
        <div className="analysis-card">
          <h2>Job Clusters</h2>
          <div className="cluster-list">
            {clusters.map((cluster, idx) => (
              <div key={idx} className="cluster-item">
                <div className="cluster-header">
                  <span className="cluster-label" style={{ background: COLORS[idx % COLORS.length] }}>
                    Cluster {cluster.cluster_id}
                  </span>
                  <span className="cluster-count">{cluster.job_count} jobs</span>
                </div>
                <div className="cluster-keywords">
                  {cluster.top_keywords.slice(0, 8).join(' • ')}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Topic Modeling */}
        <div className="analysis-card">
          <h2>Topic Distribution</h2>
          <div className="topics-list">
            {topics.map((topic, idx) => (
              <div key={idx} className="topic-item">
                <div className="topic-header">
                  <span className="topic-label">Topic {topic.topic_id}</span>
                  <span className="topic-weight">{(topic.weight * 100).toFixed(1)}%</span>
                </div>
                <div className="topic-bar">
                  <div 
                    className="topic-fill" 
                    style={{ 
                      width: `${topic.weight * 100}%`,
                      background: COLORS[idx % COLORS.length]
                    }}
                  />
                </div>
                <div className="topic-keywords">
                  {topic.keywords.slice(0, 6).join(', ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Job Description Analyzer */}
      <div className="analyzer-section">
        <h2>Analyze Job Description</h2>
        <p className="section-subtitle">Paste a job description to predict its cluster, topics, and extract key skills</p>
        
        <textarea
          className="job-input"
          placeholder="Paste job description here..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={8}
        />
        
        <button 
          className="analyze-button"
          onClick={handleAnalyze}
          disabled={analyzing || !jobDescription.trim()}
        >
          {analyzing ? 'Analyzing...' : 'Analyze Job Description'}
        </button>

        {prediction && (
          <div className="prediction-results">
            <div className="result-card">
              <h3>Predicted Cluster</h3>
              <div className="cluster-prediction">
                <span className="cluster-badge" style={{ background: COLORS[prediction.cluster.cluster_id % COLORS.length] }}>
                  Cluster {prediction.cluster.cluster_id}
                </span>
                <span className="confidence">Confidence: {(prediction.cluster.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="cluster-description">
                <strong>Common skills in this cluster:</strong>
                <p>{prediction.cluster.description}</p>
              </div>
            </div>

            <div className="result-card">
              <h3>Topic Distribution</h3>
              {prediction.topic.topics.map((topic, idx) => (
                <div key={idx} className="topic-prediction-item">
                  <div className="topic-name">Topic {topic.topic_id}</div>
                  <div className="topic-bar">
                    <div 
                      className="topic-fill" 
                      style={{ 
                        width: `${topic.probability * 100}%`,
                        background: COLORS[idx % COLORS.length]
                      }}
                    />
                  </div>
                  <span className="topic-percentage">{(topic.probability * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>

            <div className="result-card">
              <h3>Extracted Skills</h3>
              <div className="skills-grid">
                {prediction.skills.skills.map((skill, idx) => (
                  <span key={idx} className="skill-badge">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Analysis;
