import { useState } from "react";
import API from "./services/api";

function App() {
  const [resumes, setResumes] = useState([]);
  const [jobDescription, setJobDescription] = useState("");
  const [results, setResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (resumes.length === 0 || !jobDescription.trim()) {
      setError("Please upload at least one resume and enter a job description.");
      return;
    }

    setError("");
    setLoading(true);
    setResults([]);
    setSelectedResult(null);

    const formData = new FormData();
    resumes.forEach((file) => {
      formData.append("resumes", file);
    });
    formData.append("job_description", jobDescription);

    try {
      const response = await API.post("/analyze-multiple", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResults(response.data.results);
      if (response.data.results.length > 0) {
        setSelectedResult(response.data.results[0]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setResumes((prev) => {
      // Avoid adding exact same file objects if possible, though browser file objects are unique per pick
      // Let's filter by name to be simple (assuming different names for different resumes)
      const existingNames = prev.map(f => f.name);
      const uniqueNewFiles = newFiles.filter(f => !existingNames.includes(f.name));
      return [...prev, ...uniqueNewFiles];
    });
  };

  const removeFile = (index) => {
    setResumes((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="container">
      <header className="header">
        <h1>AI Resume Ranking System</h1>
        <p className="subtitle">Upload multiple CVs to find the best match for your job description</p>
      </header>

      <main className="main-content">
        <div className="input-section card">
          <div className="input-group">
            <label className="label">Upload Resumes (PDF/DOCX)</label>
            <div className="file-input-wrapper">
              <input
                type="file"
                className="file-input"
                accept=".pdf,.docx"
                multiple
                onChange={handleFileChange}
                id="resume-upload"
              />
              <label htmlFor="resume-upload" className="file-label">
                {resumes.length > 0 ? `${resumes.length} files selected` : "Choose Files"}
              </label>
            </div>
            {resumes.length > 0 && (
              <div className="file-list">
                {resumes.map((f, i) => (
                  <span key={i} className="file-tag">
                    {f.name}
                    <button className="remove-file-btn" onClick={() => removeFile(i)}>×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="input-group">
            <label className="label">Job Description</label>
            <textarea
              className="textarea"
              rows="6"
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
              "Rank Resumes"
            )}
          </button>

          {error && <div className="error-message">{error}</div>}
        </div>

        {results.length > 0 && (
          <div className="ranking-section fade-in">
            <div className="ranking-card card">
              <h3>Resume Ranking</h3>
              <div className="ranking-table-container">
                <table className="ranking-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Filename</th>
                      <th>Score</th>
                      <th>Recommendation</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((res, index) => (
                      <tr 
                        key={index} 
                        className={selectedResult?.filename === res.filename ? 'selected' : ''}
                        onClick={() => setSelectedResult(res)}
                      >
                        <td>{index + 1}</td>
                        <td className="filename-cell">{res.filename}</td>
                        <td>
                          <span className={`score-badge ${res.match_score >= 80 ? 'good' : res.match_score >= 50 ? 'okay' : 'poor'}`}>
                            {res.match_score.toFixed(0)}%
                          </span>
                        </td>
                        <td>{res.recommendation}</td>
                        <td>
                          <button className="view-btn">View Details</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {selectedResult && (
          <div className="result-section fade-in">
            <div className="section-title">
              <h2>Detailed Analysis for: <span className="highlight">{selectedResult.filename}</span></h2>
            </div>
            <div className="score-card card">
              <div className="match-score-circle">
                <svg viewBox="0 0 36 36" className="circular-chart">
                  <path className="circle-bg"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path className={`circle ${selectedResult.match_score >= 80 ? 'good' : selectedResult.match_score >= 50 ? 'okay' : 'poor'}`}
                    strokeDasharray={`${selectedResult.match_score}, 100`}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <text x="18" y="20.35" className="percentage">{selectedResult.match_score.toFixed(0)}%</text>
                </svg>
                <div className="score-label">Overall Match</div>
              </div>

              <div className="progress-bar-container">
                <div className="progress-label">Confidence Level</div>
                <div className="progress-track">
                   <div 
                    className={`progress-fill ${selectedResult.match_score >= 80 ? 'good' : selectedResult.match_score >= 50 ? 'okay' : 'poor'}`} 
                    style={{ width: `${selectedResult.match_score}%` }}
                   ></div>
                </div>
              </div>

              <div className="recommendation-badge">
                 <span className={`badge ${selectedResult.recommendation.toLowerCase().replace(/ /g, "-")}`}>
                   {selectedResult.recommendation}
                 </span>
              </div>
            </div>

            <div className="analysis-summary card">
              <div className="analysis-horizontal-layout">
                <div className="analysis-col">
                  <h3 className="ai-heading"><span className="sparkle-icon">✨</span> AI-Powered Detailed Analysis</h3>
                  <p className="explanation-text ai-text">{selectedResult.ai_explanation || "Generating AI analysis..."}</p>
                </div>
                <div className="analysis-col">
                  <h3>Why this score?</h3>
                  <p className="explanation-text standard-text">{selectedResult.explanation}</p>
                </div>
              </div>
              
              <div className="insights-list">
                {selectedResult.insights.map((insight, i) => (
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
                    {selectedResult.matched_skills.map((s, i) => (
                      <span key={i} className="tag matched">{s}</span>
                    ))}
                    {selectedResult.matched_skills.length === 0 && <span className="empty">None</span>}
                  </div>
                </div>

                <div className="skill-item">
                  <span className="skill-label">Missing Skills</span>
                  <div className="skill-tags">
                    {selectedResult.missing_skills.map((s, i) => (
                      <span key={i} className="tag missing">{s}</span>
                    ))}
                    {selectedResult.missing_skills.length === 0 && <span className="empty">None</span>}
                  </div>
                </div>
              </div>

              {selectedResult.interview_questions && (
                <div className="interview-section">
                  <div className="divider"></div>
                  <h3>Suggested Interview Questions</h3>
                  <div className="explanation-text ai-text questions-box">
                    {selectedResult.interview_questions || "N/A"}
                  </div>
                </div>
              )}

            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;