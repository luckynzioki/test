const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  async submitGeneration(prompt, options = {}) {
    const response = await fetch(`${API_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        duration: options.duration || 5,
        height: options.height || 720,
        width: options.width || 1280,
        fps: options.fps || 24,
        num_inference_steps: options.steps || 50,
      }),
    });

    if (!response.ok) throw new Error('Generation submission failed');
    return response.json();
  },

  async getJobStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/api/job/${jobId}`);
    if (!response.ok) throw new Error('Failed to fetch job status');
    return response.json();
  },

  async listJobs(limit = 50) {
    const response = await fetch(`${API_BASE_URL}/api/jobs?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch jobs');
    return response.json();
  },

  async getHealth() {
    const response = await fetch(`${API_BASE_URL}/`);
    if (!response.ok) throw new Error('API unavailable');
    return response.json();
  },

  getVideoDownloadUrl(jobId) {
    return `${API_BASE_URL}/api/job/${jobId}/video`;
  },

  getAudioDownloadUrl(jobId) {
    return `${API_BASE_URL}/api/job/${jobId}/audio`;
  },
};
