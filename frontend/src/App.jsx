import { useState } from "react";
import API from "./services/api";

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!resume || !jobDescription.trim()) {
      setError("Please upload a resume and enter a job description.");
      return;
    }

    setError("");
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    try {
      const response = await API.post("/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>AI Resume Matcher</h1>
        <p className="subtitle">Analyze your CV against job descriptions with precision</p>
      </header>

      <main className="main-content">
        <div className="input-section card">
          <div className="input-group">
            <label className="label">Upload Resume (PDF/DOCX)</label>
            <div className="file-input-wrapper">
              <input
                type="file"
                className="file-input"
                accept=".pdf,.docx"
                onChange={(e) => setResume(e.target.files[0])}
                id="resume-upload"
              />
              <label htmlFor="resume-upload" className="file-label">
                {resume ? resume.name : "Choose File"}
              </label>
            </div>
          </div>

          <div className="input-group">
            <label className="label">Job Description</label>
            <textarea
              className="textarea"
              rows="8"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
            />
          </div>

          <button 
            className={`analyze-button ${loading ? 'loading' : ''}`}
            onClick={handleAnalyze} 
            disabled={loading}
          >
            {loading ? (
              <span className="spinner"></span>
            ) : (
              "Analyze CV"
            )}
          </button>

          {error && <div className="error-message">{error}</div>}
        </div>

        {result && (
          <div className="result-section fade-in">
            <div className="score-card card">
              <div className="match-score-circle">
                <svg viewBox="0 0 36 36" className="circular-chart">
                  <path className="circle-bg"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path className={`circle ${result.match_score >= 80 ? 'good' : result.match_score >= 50 ? 'okay' : 'poor'}`}
                    strokeDasharray={`${result.match_score}, 100`}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <text x="18" y="20.35" className="percentage">{result.match_score.toFixed(0)}%</text>
                </svg>
                <div className="score-label">Overall Match</div>
              </div>

              <div className="progress-bar-container">
                <div className="progress-label">Confidence Level</div>
                <div className="progress-track">
                   <div 
                    className={`progress-fill ${result.match_score >= 80 ? 'good' : result.match_score >= 50 ? 'okay' : 'poor'}`} 
                    style={{ width: `${result.match_score}%` }}
                   ></div>
                </div>
              </div>

              <div className="recommendation-badge">
                 <span className={`badge ${result.recommendation.toLowerCase().replace(/ /g, "-")}`}>
                   {result.recommendation}
                 </span>
              </div>
            </div>

            <div className="analysis-summary card">
              <h3>Why this score?</h3>
              <p className="explanation-text">{result.explanation}</p>
              
              <div className="insights-list">
                {result.insights.map((insight, i) => (
                  <div key={i} className="insight-item">
                    <span className="insight-icon">💡</span>
                    <span>{insight}</span>
                  </div>
                ))}
              </div>

              <div className="skill-grid">
                <div className="skill-item">
                  <span className="skill-label">Matched Skills</span>
                  <div className="skill-tags">
                    {result.matched_skills.map((s, i) => (
                      <span key={i} className="tag matched">{s}</span>
                    ))}
                    {result.matched_skills.length === 0 && <span className="empty">None</span>}
                  </div>
                </div>

                <div className="skill-item">
                  <span className="skill-label">Missing Skills</span>
                  <div className="skill-tags">
                    {result.missing_skills.map((s, i) => (
                      <span key={i} className="tag missing">{s}</span>
                    ))}
                    {result.missing_skills.length === 0 && <span className="empty">None</span>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;