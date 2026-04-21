import React, { useState, useEffect } from 'react';
import { api } from '../api';

function ProgressIndicator({ jobId, onCompleted }) {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const data = await api.getJobStatus(jobId);
        setStatus(data);
        setError(null);

        if (data.status === 'completed') {
          onCompleted(jobId);
        } else if (data.status !== 'failed') {
          // Continue polling
          setTimeout(pollStatus, 1000);
        }
      } catch (err) {
        setError(err.message);
        setTimeout(pollStatus, 2000);
      }
    };

    pollStatus();
  }, [jobId, onCompleted]);

  if (!status) {
    return <div className="progress-indicator">Loading...</div>;
  }

  const getStatusColor = () => {
    switch (status.status) {
      case 'queued': return '#FF9800';
      case 'processing': return '#2196F3';
      case 'completed': return '#4CAF50';
      case 'failed': return '#F44336';
      default: return '#999';
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'queued': return '⏳ Waiting to start...';
      case 'processing': return '⚙️ Generating video...';
      case 'completed': return '✅ Complete!';
      case 'failed': return '❌ Failed';
      default: return status.status;
    }
  };

  return (
    <div className="progress-indicator">
      <div className="status-header">
        <h3>Generation Status</h3>
        <span style={{ color: getStatusColor() }}>{getStatusText()}</span>
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{
            width: `${Math.min(status.progress * 100, 100)}%`,
            backgroundColor: getStatusColor(),
          }}
        />
      </div>

      <p className="progress-text">
        {Math.round(status.progress * 100)}% complete
      </p>

      <div className="status-details">
        <p><strong>Job ID:</strong> {jobId.slice(0, 8)}...</p>
        <p><strong>Prompt:</strong> {status.prompt.slice(0, 60)}...</p>
        {status.duration_seconds && (
          <p><strong>Time Elapsed:</strong> {Math.round(status.duration_seconds)}s</p>
        )}
      </div>

      {error && <div className="error-message">⚠️ {error}</div>}
      {status.error && <div className="error-message">❌ {status.error}</div>}
    </div>
  );
}

export default ProgressIndicator;
