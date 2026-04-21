import React, { useState } from 'react';
import { api } from '../api';

function GenerationForm({ onJobSubmitted }) {
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(5);
  const [quality, setQuality] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const qualitySettings = {
    low: { steps: 20, height: 480, width: 640 },
    medium: { steps: 50, height: 720, width: 1280 },
    high: { steps: 75, height: 1080, width: 1920 },
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (!prompt.trim()) {
        throw new Error('Please enter a prompt');
      }

      const settings = qualitySettings[quality];
      const result = await api.submitGeneration(prompt, {
        duration,
        ...settings,
      });

      onJobSubmitted(result.job_id);
      setPrompt('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="generation-form">
      <h2>Generate Video</h2>

      <div className="form-group">
        <label>What would you like to create?</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="A golden retriever playing fetch in a sunny park..."
          disabled={loading}
          rows="4"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Duration (seconds)</label>
          <input
            type="range"
            min="1"
            max="20"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            disabled={loading}
          />
          <span className="form-value">{duration}s</span>
        </div>

        <div className="form-group">
          <label>Quality</label>
          <select
            value={quality}
            onChange={(e) => setQuality(e.target.value)}
            disabled={loading}
          >
            <option value="low">Fast (480p, 20s steps)</option>
            <option value="medium">Balanced (720p, 50 steps)</option>
            <option value="high">High Quality (1080p, 75 steps)</option>
          </select>
        </div>
      </div>

      {error && <div className="error-message">❌ {error}</div>}

      <button type="submit" disabled={loading || !prompt.trim()} className="btn-primary">
        {loading ? 'Queuing...' : '✨ Generate Video'}
      </button>

      <p className="form-hint">
        💡 Typical generation time: 1-3 minutes on RTX 4090
      </p>
    </form>
  );
}

export default GenerationForm;
