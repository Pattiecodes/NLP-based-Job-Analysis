import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FiRefreshCw } from 'react-icons/fi';
import './Home.css';

function Home() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  useEffect(() => {
    fetchHomeData();
  }, []);

  const fetchHomeData = async () => {
    try {
      const [statsRes, skillsRes, newsRes] = await Promise.all([
        axios.get('/api/dashboard/stats'),
        axios.get('/api/dashboard/top-skills'),
        axios.get('/api/scraping/news/latest?limit=5')
      ]);
      
      setStats(statsRes.data);
      setNews(newsRes.data.news || []);
      
      // Prepare chart data from top skills
      const topSkillsForChart = (skillsRes.data.skills || []).slice(0, 7).map((skill, index) => ({
        name: skill.Skill,
        value: skill.Count
      }));
      setChartData(topSkillsForChart);
    } catch (error) {
      console.error('Error fetching home data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeNews = async () => {
    try {
      setScraping(true);
      await axios.post('/api/scraping/news/trigger');
      // Refresh news after scraping
      const newsRes = await axios.get('/api/scraping/news/latest?limit=5');
      setNews(newsRes.data.news || []);
    } catch (error) {
      console.error('Error scraping news:', error);
    } finally {
      setScraping(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="home-container">
      <div className="greeting-section">
        <h1>Hello, {user ? user.username : 'User'}!</h1>
        <p className="greeting-text">
          Check out news, trends, and dashboards to stay up-to-date with the latest job market insights.
        </p>
      </div>

      <div className="home-grid">
        {/* News Section */}
        <div className="home-card news-card">
          <div className="news-header">
            <h2>Tech News & Trends</h2>
            <button 
              className="scrape-btn"
              onClick={handleScrapeNews}
              disabled={scraping}
            >
              <FiRefreshCw className={scraping ? 'spinning' : ''} />
              {scraping ? 'Scraping...' : 'Refresh'}
            </button>
          </div>
          <div className="news-content">
            {news.length > 0 ? (
              news.map((article, index) => (
                <div key={index} className="news-item">
                  <h3>
                    <a href={article.link} target="_blank" rel="noopener noreferrer">
                      {article.title}
                    </a>
                  </h3>
                  <p className="news-summary">{article.summary}</p>
                  <div className="news-meta">
                    <span className="news-source">{article.source}</span>
                    <span className="news-date">
                      {new Date(article.scraped_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-news">
                <p>No news articles yet. Click "Refresh" to scrape latest tech news.</p>
              </div>
            )}
          </div>
        </div>

        {/* Explore Section with Chart */}
        <div className="home-card explore-card">
          <h2>Explore</h2>
          <div className="chart-info">
            <div className="chart-title">CHART TITLE</div>
            <div className="chart-value">{stats?.total_jobs?.toLocaleString() || '5,000.00'}</div>
            <div className="chart-caption">
              {chartData.length} Orders
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#0088FE" 
                strokeWidth={2}
                dot={{ fill: '#0088FE', r: 4 }}
                name="Count"
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#00C49F" 
                strokeWidth={2}
                dot={{ fill: '#00C49F', r: 4 }}
                name="Trend"
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
          
          <div className="chart-legend">
            <div className="legend-item">
              <span className="legend-dot" style={{ background: '#0088FE' }}></span>
              <span>Current</span>
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ background: '#00C49F' }}></span>
              <span>Current</span>
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ background: '#FFBB28' }}></span>
              <span>Current</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
