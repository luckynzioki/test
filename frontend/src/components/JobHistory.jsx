import React, { useState, useEffect } from 'react';
import { api } from '../api';

function JobHistory() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await api.listJobs(20);
        setJobs(data.jobs || []);
      } catch (err) {
        console.error('Failed to fetch jobs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⚙️';
      case 'queued': return '⏳';
      case 'failed': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="job-history">
      <h2>Recent Generations</h2>

      {loading ? (
        <p>Loading history...</p>
      ) : jobs.length === 0 ? (
        <p>No generations yet. Create one above!</p>
      ) : (
        <div className="jobs-list">
          {jobs.map((job) => (
            <div key={job.job_id} className="job-item">
              <span className="status-icon">{getStatusIcon(job.status)}</span>
              <div className="job-details">
                <p className="job-prompt">{job.prompt}</p>
                <p className="job-meta">
                  {job.status} • {job.progress ? Math.round(job.progress * 100) + '%' : 'N/A'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default JobHistory;
