import { useState } from 'react';
import axios from 'axios';
import { FiSearch, FiMapPin, FiBriefcase, FiDollarSign, FiExternalLink, FiFilter } from 'react-icons/fi';
import './SearchPage.css';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    jobLevel: '',
    jobType: '',
    location: ''
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      const params = {
        query: query,
        ...filters
      };
      
      const response = await axios.get('/api/analysis/search', { params });
      setResults(response.data.jobs || []);
    } catch (error) {
      console.error('Error searching jobs:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const highlightText = (text, query) => {
    if (!query.trim() || !text) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() 
        ? <mark key={i}>{part}</mark> 
        : part
    );
  };

  return (
    <div className="search-page">
      <h1>Job Search</h1>
      <p className="subtitle">Search through job postings and find opportunities that match your skills</p>

      <div className="search-container">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <FiSearch className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search by job title, skills, or keywords..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          <div className="filters">
            <div className="filter-group">
              <FiFilter className="filter-icon" />
              <select 
                className="filter-select"
                value={filters.jobLevel}
                onChange={(e) => handleFilterChange('jobLevel', e.target.value)}
              >
                <option value="">All Levels</option>
                <option value="Entry level">Entry Level</option>
                <option value="Mid-Senior level">Mid-Senior Level</option>
                <option value="Director">Director</option>
                <option value="Executive">Executive</option>
              </select>
            </div>

            <div className="filter-group">
              <FiBriefcase className="filter-icon" />
              <select 
                className="filter-select"
                value={filters.jobType}
                onChange={(e) => handleFilterChange('jobType', e.target.value)}
              >
                <option value="">All Types</option>
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
              </select>
            </div>

            <div className="filter-group">
              <FiMapPin className="filter-icon" />
              <input
                type="text"
                className="filter-input"
                placeholder="Location"
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
              />
            </div>
          </div>
        </form>

        <div className="results-container">
          {loading ? (
            <div className="loading">Searching jobs...</div>
          ) : searched && results.length === 0 ? (
            <div className="no-results">
              <p>No jobs found matching your search criteria.</p>
              <p className="no-results-tip">Try different keywords or adjust your filters.</p>
            </div>
          ) : results.length > 0 ? (
            <>
              <div className="results-header">
                <h2>Found {results.length} job{results.length !== 1 ? 's' : ''}</h2>
              </div>
              <div className="results-list">
                {results.map((job, idx) => (
                  <div key={idx} className="job-card">
                    <div className="job-header">
                      <h3 className="job-title">
                        {highlightText(job.job_title, query)}
                      </h3>
                      {job.job_link && (
                        <a 
                          href={job.job_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="job-link"
                        >
                          <FiExternalLink />
                        </a>
                      )}
                    </div>

                    <div className="job-meta">
                      {job.company && (
                        <span className="meta-item">
                          <FiBriefcase />
                          {job.company}
                        </span>
                      )}
                      {job.job_location && (
                        <span className="meta-item">
                          <FiMapPin />
                          {job.job_location}
                        </span>
                      )}
                      {job.formatted_experience_level && (
                        <span className="meta-item level">
                          {job.formatted_experience_level}
                        </span>
                      )}
                      {job.formatted_work_type && (
                        <span className="meta-item type">
                          {job.formatted_work_type}
                        </span>
                      )}
                    </div>

                    {job.job_summary && (
                      <p className="job-summary">
                        {highlightText(job.job_summary.substring(0, 200) + '...', query)}
                      </p>
                    )}

                    {job.skills && job.skills.length > 0 && (
                      <div className="job-skills">
                        {job.skills.slice(0, 8).map((skill, skillIdx) => (
                          <span key={skillIdx} className="skill-tag">
                            {skill}
                          </span>
                        ))}
                        {job.skills.length > 8 && (
                          <span className="skill-more">+{job.skills.length - 8} more</span>
                        )}
                      </div>
                    )}

                    {job.min_salary && job.max_salary && (
                      <div className="job-salary">
                        <FiDollarSign />
                        ${job.min_salary.toLocaleString()} - ${job.max_salary.toLocaleString()}
                        {job.pay_period && ` / ${job.pay_period}`}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="search-empty">
              <FiSearch className="empty-icon" />
              <h3>Start Your Job Search</h3>
              <p>Enter keywords, skills, or job titles to find relevant opportunities.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SearchPage;
