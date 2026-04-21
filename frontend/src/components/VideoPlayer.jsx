import React, { useState, useEffect } from 'react';
import { api } from '../api';

function VideoPlayer({ jobId }) {
  const [status, setStatus] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await api.getJobStatus(jobId);
        setStatus(data);
      } catch (err) {
        console.error('Failed to fetch status:', err);
      }
    };

    fetchStatus();
  }, [jobId]);

  if (!status || status.status !== 'completed') {
    return null;
  }

  return (
    <div className="video-player">
      <h3>Your Video</h3>

      {showPreview && status.video_url ? (
        <div className="video-preview">
          <video
            controls
            src={api.getVideoDownloadUrl(jobId)}
            style={{ width: '100%', borderRadius: '8px' }}
          />
        </div>
      ) : (
        <div className="video-placeholder">
          <p>🎥 Video ready</p>
          <button
            onClick={() => setShowPreview(true)}
            className="btn-secondary"
          >
            Preview Video
          </button>
        </div>
      )}

      <div className="download-buttons">
        <a
          href={api.getVideoDownloadUrl(jobId)}
          download={`ai-video-${jobId.slice(0, 8)}.mp4`}
          className="btn-download"
        >
          ⬇️ Download Video (MP4)
        </a>
        {status.audio_url && (
          <a
            href={api.getAudioDownloadUrl(jobId)}
            download={`ai-audio-${jobId.slice(0, 8)}.wav`}
            className="btn-download"
          >
            ⬇️ Download Audio (WAV)
          </a>
        )}
      </div>
    </div>
  );
}

export default VideoPlayer;
