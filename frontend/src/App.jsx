import React, { useState } from 'react';
import GenerationForm from './components/GenerationForm';
import ProgressIndicator from './components/ProgressIndicator';
import VideoPlayer from './components/VideoPlayer';
import JobHistory from './components/JobHistory';
import './App.css';

function App() {
  const [currentJobId, setCurrentJobId] = useState(null);
  const [completedJobs, setCompletedJobs] = useState([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleJobSubmitted = (jobId) => {
    setCurrentJobId(jobId);
  };

  const handleJobCompleted = (jobId) => {
    setCompletedJobs(prev => [...prev, jobId]);
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🎬 AI Video Studio</h1>
          <p>Professional-grade video generation with AI. Local. Open-source. No limits.</p>
        </div>
      </header>

      <main className="container">
        <div className="layout">
          {/* Left: Generation Form */}
          <section className="panel generation-panel">
            <GenerationForm onJobSubmitted={handleJobSubmitted} />
          </section>

          {/* Right: Progress & Output */}
          <section className="panel output-panel">
            {currentJobId ? (
              <>
                <ProgressIndicator jobId={currentJobId} onCompleted={handleJobCompleted} />
                <VideoPlayer jobId={currentJobId} />
              </>
            ) : (
              <div className="placeholder">
                <p>📝 Enter a prompt and click "Generate" to create your first video</p>
                <p style={{ fontSize: '12px', marginTop: '8px', color: '#999' }}>
                  Examples: "A cat sleeping on a sunny windowsill" or "A woman walking through a rainy city"
                </p>
              </div>
            )}
          </section>
        </div>

        {/* History */}
        <section className="panel history-panel">
          <JobHistory key={refreshTrigger} />
        </section>
      </main>

      <footer className="footer">
        <p>Made with ❤️ using open-source AI models • <a href="#" onClick={() => alert('View API docs at http://localhost:8000/docs')}>API Docs</a></p>
      </footer>
    </div>
  );
}

export default App;
