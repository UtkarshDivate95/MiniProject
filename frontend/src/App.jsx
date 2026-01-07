import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
    // State management
    const [file, setFile] = useState(null)
    const [jobDescription, setJobDescription] = useState('')
    const [results, setResults] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [dragOver, setDragOver] = useState(false)
    const [theme, setTheme] = useState('dark')
    const [activeView, setActiveView] = useState('analyzer')
    const [activeTab, setActiveTab] = useState('overview')
    const [tips, setTips] = useState([])
    const [industries, setIndustries] = useState({})
    const [selectedIndustry, setSelectedIndustry] = useState('')
    const [history, setHistory] = useState([])
    const [sampleJobs, setSampleJobs] = useState([])
    const [copyNotification, setCopyNotification] = useState('')
    const [showResumePreview, setShowResumePreview] = useState(false)

    const fileInputRef = useRef(null)

    // Fetch tips and industry keywords on mount
    useEffect(() => {
        fetchTips()
        fetchIndustries()
        fetchHistory()
        fetchSampleJobs()
    }, [])

    // Apply theme
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme)
    }, [theme])

    const fetchTips = async () => {
        try {
            const response = await axios.get(`${API_URL}/tips`)
            setTips(response.data.tips || [])
        } catch (err) {
            console.error('Failed to fetch tips:', err)
        }
    }

    const fetchIndustries = async () => {
        try {
            const response = await axios.get(`${API_URL}/industries`)
            setIndustries(response.data.industries || {})
        } catch (err) {
            console.error('Failed to fetch industries:', err)
        }
    }

    const fetchHistory = async () => {
        try {
            const response = await axios.get(`${API_URL}/history`)
            setHistory(response.data.history || [])
        } catch (err) {
            console.error('Failed to fetch history:', err)
        }
    }

    const fetchSampleJobs = async () => {
        try {
            const response = await axios.get(`${API_URL}/sample-jobs`)
            setSampleJobs(response.data.samples || [])
        } catch (err) {
            console.error('Failed to fetch sample jobs:', err)
        }
    }

    // Copy to clipboard helper
    const copyToClipboard = async (text, label) => {
        try {
            await navigator.clipboard.writeText(text)
            setCopyNotification(`${label} copied to clipboard!`)
            setTimeout(() => setCopyNotification(''), 2500)
        } catch (err) {
            console.error('Failed to copy:', err)
            setCopyNotification('Failed to copy')
            setTimeout(() => setCopyNotification(''), 2500)
        }
    }

    // Load sample job description
    const loadSampleJob = (jobId) => {
        const job = sampleJobs.find(j => j.id === jobId)
        if (job) {
            setJobDescription(job.description)
        }
    }

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0]
        if (selectedFile) {
            validateAndSetFile(selectedFile)
        }
    }

    const validateAndSetFile = (selectedFile) => {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if (validTypes.includes(selectedFile.type) || selectedFile.name.endsWith('.pdf') || selectedFile.name.endsWith('.docx')) {
            setFile(selectedFile)
            setError('')
        } else {
            setError('Please upload a PDF or DOCX file.')
            setFile(null)
        }
    }

    const handleDragOver = (e) => {
        e.preventDefault()
        setDragOver(true)
    }

    const handleDragLeave = () => {
        setDragOver(false)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setDragOver(false)
        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile) {
            validateAndSetFile(droppedFile)
        }
    }

    const handleRemoveFile = (e) => {
        e.stopPropagation()
        setFile(null)
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    const handleSubmit = async () => {
        if (!file || !jobDescription.trim()) {
            setError('Please upload a resume and enter a job description.')
            return
        }

        setLoading(true)
        setError('')
        setResults(null)

        const formData = new FormData()
        formData.append('resume', file)
        formData.append('job_description', jobDescription)

        try {
            const response = await axios.post(`${API_URL}/analyze`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            })
            setResults(response.data)
            fetchHistory() // Refresh history
        } catch (err) {
            console.error(err)
            setError(err.response?.data?.detail || 'An error occurred while analyzing your resume.')
        } finally {
            setLoading(false)
        }
    }

    const handleIndustryChange = (e) => {
        const industry = e.target.value
        setSelectedIndustry(industry)
        if (industry && industries[industry]) {
            const keywords = industries[industry].keywords.join(', ')
            const currentText = jobDescription.trim()
            if (currentText) {
                setJobDescription(`${currentText}\n\nKey skills: ${keywords}`)
            } else {
                setJobDescription(`Looking for a candidate with expertise in: ${keywords}`)
            }
        }
    }

    const getScoreColor = (score) => {
        if (score >= 75) return 'var(--success)'
        if (score >= 50) return 'var(--warning)'
        return 'var(--error)'
    }

    const CircularProgress = ({ value, size = 120 }) => {
        const radius = 52
        const circumference = 2 * Math.PI * radius
        const offset = circumference - (value / 100) * circumference

        return (
            <div className="circular-progress" style={{ width: size, height: size }}>
                <svg width={size} height={size} viewBox="0 0 120 120">
                    <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#8b5cf6" />
                            <stop offset="50%" stopColor="#6366f1" />
                            <stop offset="100%" stopColor="#3b82f6" />
                        </linearGradient>
                    </defs>
                    <circle
                        className="circular-progress__bg"
                        cx="60"
                        cy="60"
                        r={radius}
                    />
                    <circle
                        className="circular-progress__fill"
                        cx="60"
                        cy="60"
                        r={radius}
                        style={{ strokeDashoffset: offset }}
                    />
                </svg>
                <div className="circular-progress__value">{value}%</div>
            </div>
        )
    }

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString()
    }

    const renderAnalyzer = () => (
        <>
            <div className="main-grid">
                {/* Upload Card */}
                <div className="card">
                    <div className="card__header">
                        <h2 className="card__title">
                            <span className="card__title-icon">📄</span>
                            Upload Resume
                        </h2>
                        <span className="card__badge">PDF / DOCX</span>
                    </div>
                    <div
                        className={`upload-zone ${dragOver ? 'dragover' : ''}`}
                        onClick={() => fileInputRef.current?.click()}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept=".pdf,.docx"
                            style={{ display: 'none' }}
                        />
                        {file ? (
                            <div className="upload-zone__file">
                                <div className="upload-zone__file-info">
                                    <span className="upload-zone__file-icon">📄</span>
                                    <span>{file.name}</span>
                                </div>
                                <button className="upload-zone__remove" onClick={handleRemoveFile}>
                                    Remove File
                                </button>
                            </div>
                        ) : (
                            <>
                                <div className="upload-zone__icon">📤</div>
                                <p className="upload-zone__text">Drag & drop your resume here or click to browse</p>
                                <p className="upload-zone__formats">Supported formats: PDF, DOCX (max 5MB)</p>
                            </>
                        )}
                    </div>
                </div>

                {/* Job Description Card */}
                <div className="card">
                    <div className="card__header">
                        <h2 className="card__title">
                            <span className="card__title-icon">📋</span>
                            Job Description
                        </h2>
                        <span className="card__badge">{jobDescription.length} chars</span>
                    </div>
                    <div className="textarea-wrapper">
                        <textarea
                            className="textarea"
                            placeholder="Paste the job description here... Include requirements, responsibilities, and desired skills for best results."
                            value={jobDescription}
                            onChange={(e) => setJobDescription(e.target.value)}
                        />
                    </div>

                    {/* Sample Job Descriptions */}
                    <div className="quick-actions">
                        <div className="industry-select">
                            <label className="industry-select__label">📄 Load Sample Job Description:</label>
                            <select
                                value=""
                                onChange={(e) => loadSampleJob(e.target.value)}
                            >
                                <option value="">Select a sample job...</option>
                                {sampleJobs.map((job) => (
                                    <option key={job.id} value={job.id}>
                                        {job.title} @ {job.company}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="industry-select">
                            <label className="industry-select__label">✨ Quick Add Industry Keywords:</label>
                            <select value={selectedIndustry} onChange={handleIndustryChange}>
                                <option value="">Select an industry...</option>
                                {Object.entries(industries).map(([key, value]) => (
                                    <option key={key} value={key}>{value.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {jobDescription.length > 0 && (
                        <button
                            className="btn btn--secondary btn--small"
                            onClick={() => setJobDescription('')}
                            style={{ marginTop: '0.5rem' }}
                        >
                            🗑️ Clear Job Description
                        </button>
                    )}
                </div>
            </div>

            <div className="analyze-section">
                <button
                    className="btn btn--primary"
                    onClick={handleSubmit}
                    disabled={loading || !file || !jobDescription.trim()}
                >
                    {loading ? (
                        <>
                            <span className="spinner"></span> Analyzing...
                        </>
                    ) : (
                        <>🔍 Analyze Resume</>
                    )}
                </button>
            </div>

            {error && (
                <div className="error">
                    <span>⚠️</span> {error}
                </div>
            )}

            {loading && (
                <div className="loading-screen">
                    <div className="loading-spinner-large"></div>
                    <p className="loading-text">Analyzing your resume...</p>
                    <p className="loading-subtext">Checking keywords, structure, and formatting</p>
                </div>
            )}

            {results && !loading && renderResults()}
        </>
    )

    const renderResults = () => (
        <div className="results">
            <div className="results__header">
                <h2 className="results__title">📊 Analysis Results</h2>
                <div className="results__meta">
                    <span className="results__meta-item">
                        📄 {results.filename}
                    </span>
                    <span className="results__meta-item">
                        🕐 {formatDate(results.analyzed_at)}
                    </span>
                    <span className="results__meta-item">
                        📝 {results.word_count} words
                    </span>
                </div>
            </div>

            {/* Score Grid */}
            <div className="score-grid">
                <div className="score-card score-card--main">
                    <CircularProgress value={results.overall_score} />
                    <div className="score-card__label">Overall ATS Score</div>
                    <div className="score-card__sublabel">Combined analysis of all factors</div>
                </div>
                <div className="score-card">
                    <div className="score-card__value">{results.ats_score}%</div>
                    <div className="score-card__label">Keyword Match</div>
                </div>
                <div className="score-card">
                    <div className="score-card__value">{results.section_score}%</div>
                    <div className="score-card__label">Structure Score</div>
                </div>
                <div className="score-card">
                    <div className="score-card__value">{results.formatting_score}%</div>
                    <div className="score-card__label">Formatting Score</div>
                </div>
                <div className="score-card">
                    <div className="score-card__value">{results.content_similarity_score}%</div>
                    <div className="score-card__label">Content Similarity</div>
                </div>
            </div>

            {/* Analysis Tabs */}
            <div className="analysis-tabs">
                <button
                    className={`analysis-tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    📋 Overview
                </button>
                <button
                    className={`analysis-tab ${activeTab === 'priority' ? 'active' : ''}`}
                    onClick={() => setActiveTab('priority')}
                >
                    🎯 Priority Actions
                </button>
                <button
                    className={`analysis-tab ${activeTab === 'keywords' ? 'active' : ''}`}
                    onClick={() => setActiveTab('keywords')}
                >
                    🔑 Keywords
                </button>
                <button
                    className={`analysis-tab ${activeTab === 'sections' ? 'active' : ''}`}
                    onClick={() => setActiveTab('sections')}
                >
                    📑 Sections
                </button>
                <button
                    className={`analysis-tab ${activeTab === 'density' ? 'active' : ''}`}
                    onClick={() => setActiveTab('density')}
                >
                    📊 Keyword Density
                </button>
                <button
                    className={`analysis-tab ${activeTab === 'resume' ? 'active' : ''}`}
                    onClick={() => setActiveTab('resume')}
                >
                    📄 Resume Preview
                </button>
                <button
                    className={`analysis-tab ${activeTab === 'suggestions' ? 'active' : ''}`}
                    onClick={() => setActiveTab('suggestions')}
                >
                    💡 All Suggestions
                </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && renderOverviewTab()}
            {activeTab === 'priority' && renderPriorityTab()}
            {activeTab === 'keywords' && renderKeywordsTab()}
            {activeTab === 'sections' && renderSectionsTab()}
            {activeTab === 'density' && renderDensityTab()}
            {activeTab === 'resume' && renderResumePreviewTab()}
            {activeTab === 'suggestions' && renderSuggestionsTab()}

            {/* Export Section */}
            <div className="export-section">
                <button className="btn btn--secondary" onClick={() => window.print()}>
                    🖨️ Print Report
                </button>
                <button className="btn btn--secondary" onClick={() => {
                    const data = JSON.stringify(results, null, 2)
                    const blob = new Blob([data], { type: 'application/json' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `ats-analysis-${results.filename}.json`
                    a.click()
                }}>
                    📥 Export JSON
                </button>
            </div>
        </div>
    )

    const renderOverviewTab = () => (
        <>
            {/* Skills Categories */}
            {results.skill_categories && (
                <div className="skills-categories">
                    {results.skill_categories.technical?.length > 0 && (
                        <div className="skill-category">
                            <h4 className="skill-category__title">💻 Technical Skills</h4>
                            <div className="skill-category__list">
                                {results.skill_categories.technical.map((skill, i) => (
                                    <span key={i} className="skill-category__tag">{skill}</span>
                                ))}
                            </div>
                        </div>
                    )}
                    {results.skill_categories.soft_skills?.length > 0 && (
                        <div className="skill-category">
                            <h4 className="skill-category__title">🤝 Soft Skills</h4>
                            <div className="skill-category__list">
                                {results.skill_categories.soft_skills.map((skill, i) => (
                                    <span key={i} className="skill-category__tag">{skill}</span>
                                ))}
                            </div>
                        </div>
                    )}
                    {results.skill_categories.tools?.length > 0 && (
                        <div className="skill-category">
                            <h4 className="skill-category__title">🛠️ Tools & Platforms</h4>
                            <div className="skill-category__list">
                                {results.skill_categories.tools.map((skill, i) => (
                                    <span key={i} className="skill-category__tag">{skill}</span>
                                ))}
                            </div>
                        </div>
                    )}
                    {results.skill_categories.certifications?.length > 0 && (
                        <div className="skill-category">
                            <h4 className="skill-category__title">🏆 Certifications</h4>
                            <div className="skill-category__list">
                                {results.skill_categories.certifications.map((skill, i) => (
                                    <span key={i} className="skill-category__tag">{skill}</span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Formatting Issues */}
            {results.formatting_issues && results.formatting_issues.length > 0 && (
                <div className="suggestions-card">
                    <h3 className="suggestions-card__title">📝 Formatting Analysis</h3>
                    <ul className="suggestions-list">
                        {results.formatting_issues.map((issue, index) => (
                            <li
                                key={index}
                                className={`suggestion-item suggestion-item--${issue.type === 'error' ? 'high' : issue.type === 'warning' ? 'medium' : 'low'}`}
                            >
                                <div className="suggestion-item__header">
                                    <span className={`suggestion-item__priority suggestion-item__priority--${issue.type === 'error' ? 'high' : issue.type === 'warning' ? 'medium' : 'low'}`}>
                                        {issue.type === 'success' ? '✓' : issue.type === 'error' ? '✗' : '!'} {issue.type}
                                    </span>
                                </div>
                                <p className="suggestion-item__description">{issue.message}</p>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </>
    )

    const renderPriorityTab = () => (
        <div className="priority-actions">
            <div className="priority-header">
                <h3>🎯 Top Priority Actions</h3>
                <p>Focus on these key improvements to boost your ATS score the most.</p>
            </div>

            {results.top_priority_actions && results.top_priority_actions.length > 0 ? (
                <div className="priority-list">
                    {results.top_priority_actions.map((action, index) => (
                        <div key={index} className={`priority-item priority-item--${action.priority}`}>
                            <div className="priority-item__number">{index + 1}</div>
                            <div className="priority-item__content">
                                <div className="priority-item__header">
                                    <span className={`priority-badge priority-badge--${action.priority}`}>
                                        {action.priority.toUpperCase()}
                                    </span>
                                    <span className="priority-item__category">{action.category}</span>
                                </div>
                                <h4 className="priority-item__title">{action.title}</h4>
                                <p className="priority-item__description">{action.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <div className="empty-state__icon">🎉</div>
                    <p className="empty-state__text">Your resume looks great! No critical issues found.</p>
                </div>
            )}

            {/* Quick Stats */}
            <div className="priority-stats">
                <div className="priority-stat-item">
                    <span className="priority-stat-item__icon">📊</span>
                    <span className="priority-stat-item__label">Overall Score:</span>
                    <span className="priority-stat-item__value" style={{ color: results.overall_score >= 70 ? 'var(--success)' : results.overall_score >= 50 ? 'var(--warning)' : 'var(--error)' }}>
                        {results.overall_score}%
                    </span>
                </div>
                <div className="priority-stat-item">
                    <span className="priority-stat-item__icon">🔑</span>
                    <span className="priority-stat-item__label">Keywords to Add:</span>
                    <span className="priority-stat-item__value">{results.missing_keywords?.length || 0}</span>
                </div>
                <div className="priority-stat-item">
                    <span className="priority-stat-item__icon">📝</span>
                    <span className="priority-stat-item__label">Total Suggestions:</span>
                    <span className="priority-stat-item__value">{results.suggestions?.length || 0}</span>
                </div>
            </div>
        </div>
    )

    const renderResumePreviewTab = () => (
        <div className="resume-preview">
            <div className="resume-preview__header">
                <h3>📄 Extracted Resume Text</h3>
                <p>This is how the ATS system reads your resume. Review for parsing accuracy.</p>
            </div>

            <div className="resume-preview__stats">
                <span className="resume-preview__stat">
                    📝 <strong>{results.word_count}</strong> words
                </span>
                <span className="resume-preview__stat">
                    📄 <strong>{results.filename}</strong>
                </span>
            </div>

            {results.resume_text_preview ? (
                <>
                    <div className="resume-preview__content">
                        <pre>{results.resume_text_preview}</pre>
                    </div>
                    <div className="resume-preview__actions">
                        <button
                            className="btn btn--secondary"
                            onClick={() => copyToClipboard(results.resume_text_preview, 'Resume text')}
                        >
                            📋 Copy Resume Text
                        </button>
                    </div>
                </>
            ) : (
                <div className="empty-state">
                    <div className="empty-state__icon">📭</div>
                    <p className="empty-state__text">Resume preview not available.</p>
                </div>
            )}

            <div className="resume-preview__tips">
                <h4>💡 Parsing Tips</h4>
                <ul>
                    <li>If text appears garbled, your resume may use non-standard fonts</li>
                    <li>Tables and columns may not parse correctly - consider a simpler format</li>
                    <li>Ensure your contact info is clearly parsed at the top</li>
                    <li>Check that all your skills and experience are captured</li>
                </ul>
            </div>
        </div>
    )

    const renderKeywordsTab = () => (
        <>

            {/* Keyword Match Stats */}
            {results.keyword_match_stats && (
                <div className="keyword-stats">
                    <div className="keyword-stat">
                        <div className="keyword-stat__value">{results.keyword_match_stats.total_jd_keywords}</div>
                        <div className="keyword-stat__label">Total JD Keywords</div>
                    </div>
                    <div className="keyword-stat keyword-stat--success">
                        <div className="keyword-stat__value">{results.keyword_match_stats.matched_count}</div>
                        <div className="keyword-stat__label">Matched</div>
                    </div>
                    <div className="keyword-stat keyword-stat--warning">
                        <div className="keyword-stat__value">{results.keyword_match_stats.missing_count}</div>
                        <div className="keyword-stat__label">Missing</div>
                    </div>
                    <div className="keyword-stat keyword-stat--info">
                        <div className="keyword-stat__value">{results.keyword_match_stats.match_percentage}%</div>
                        <div className="keyword-stat__label">Match Rate</div>
                    </div>
                </div>
            )}

            <div className="keywords-grid">
                <div className="keywords-card">
                    <div className="keywords-card__header">
                        <h3 className="keywords-card__title keywords-card__title--success">
                            ✅ Matched Keywords
                        </h3>
                        <span className="keywords-card__count text-success">
                            {results.matched_keywords.length}
                        </span>
                    </div>
                    <div className="keywords-list">
                        {results.matched_keywords.length > 0 ? (
                            results.matched_keywords.map((keyword, index) => (
                                <span key={index} className="keyword-tag keyword-tag--matched">
                                    {keyword}
                                </span>
                            ))
                        ) : (
                            <div className="empty-state">
                                <p className="empty-state__text">No matched keywords found</p>
                            </div>
                        )}
                    </div>
                    {results.matched_keywords.length > 0 && (
                        <button
                            className="btn btn--secondary btn--small"
                            style={{ marginTop: '1rem' }}
                            onClick={() => copyToClipboard(results.matched_keywords.join(', '), 'Matched keywords')}
                        >
                            📋 Copy All Matched
                        </button>
                    )}
                </div>
                <div className="keywords-card">
                    <div className="keywords-card__header">
                        <h3 className="keywords-card__title keywords-card__title--warning">
                            ⚠️ Missing Keywords
                        </h3>
                        <span className="keywords-card__count text-warning">
                            {results.missing_keywords.length}
                        </span>
                    </div>
                    <div className="keywords-list">
                        {results.missing_keywords.length > 0 ? (
                            results.missing_keywords.map((keyword, index) => (
                                <span key={index} className="keyword-tag keyword-tag--missing">
                                    {keyword}
                                </span>
                            ))
                        ) : (
                            <div className="empty-state">
                                <p className="empty-state__text">Great! All major keywords covered</p>
                            </div>
                        )}
                    </div>
                    {results.missing_keywords.length > 0 && (
                        <button
                            className="btn btn--primary btn--small"
                            style={{ marginTop: '1rem' }}
                            onClick={() => copyToClipboard(results.missing_keywords.join(', '), 'Missing keywords')}
                        >
                            📋 Copy All Missing Keywords
                        </button>
                    )}
                </div>
            </div>

            {/* Matched Phrases */}
            {results.matched_phrases && results.matched_phrases.length > 0 && (
                <div className="keywords-card mb-3">
                    <div className="keywords-card__header">
                        <h3 className="keywords-card__title" style={{ color: 'var(--info)' }}>
                            🔗 Matched Phrases
                        </h3>
                        <span className="keywords-card__count text-info">
                            {results.matched_phrases.length}
                        </span>
                    </div>
                    <div className="keywords-list">
                        {results.matched_phrases.map((phrase, index) => (
                            <span key={index} className="keyword-tag keyword-tag--phrase">
                                {phrase}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </>
    )


    const renderSectionsTab = () => (
        <div className="sections-grid">
            {results.sections && Object.entries(results.sections).map(([name, data]) => (
                <div key={name} className="section-item">
                    <div className={`section-item__icon ${data.present ? 'section-item__icon--present' : 'section-item__icon--missing'}`}>
                        {data.present ? '✓' : '✗'}
                    </div>
                    <div className="section-item__info">
                        <div className="section-item__name">
                            {name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </div>
                        <div className="section-item__status">
                            {data.importance} • {data.present ? 'Found' : 'Missing'}
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )

    const renderDensityTab = () => (
        <div style={{ overflowX: 'auto' }}>
            <table className="density-table">
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>In Job Description</th>
                        <th>In Resume</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {results.keyword_density && results.keyword_density.map((item, index) => (
                        <tr key={index}>
                            <td><strong>{item.keyword}</strong></td>
                            <td>{item.jd_frequency}x</td>
                            <td>{item.resume_frequency}x</td>
                            <td>
                                <span className={`density-status density-status--${item.recommendation}`}>
                                    {item.recommendation === 'good' && '✓ Good'}
                                    {item.recommendation === 'add' && '+ Add'}
                                    {item.recommendation === 'increase' && '↑ Increase'}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )

    const renderSuggestionsTab = () => (
        <div className="suggestions-card">
            <h3 className="suggestions-card__title">💡 Improvement Suggestions</h3>
            <ul className="suggestions-list">
                {results.suggestions && results.suggestions.map((suggestion, index) => (
                    <li
                        key={index}
                        className={`suggestion-item suggestion-item--${suggestion.priority}`}
                    >
                        <div className="suggestion-item__header">
                            <span className={`suggestion-item__priority suggestion-item__priority--${suggestion.priority}`}>
                                {suggestion.priority}
                            </span>
                            <span className="suggestion-item__title">{suggestion.title}</span>
                        </div>
                        <p className="suggestion-item__description">{suggestion.description}</p>
                    </li>
                ))}
            </ul>
        </div>
    )

    const renderTips = () => (
        <div>
            <div className="card">
                <h2 className="card__title">
                    <span className="card__title-icon">📚</span>
                    Resume Writing Tips
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                    Professional tips to help you write an ATS-friendly resume that gets noticed.
                </p>
            </div>
            <div className="tips-grid">
                {tips.map((tip, index) => (
                    <div key={index} className="tip-card">
                        <span className="tip-card__category">{tip.category}</span>
                        <h3 className="tip-card__title">{tip.title}</h3>
                        <p className="tip-card__description">{tip.description}</p>
                    </div>
                ))}
            </div>
        </div>
    )

    const renderHistory = () => (
        <div className="card">
            <h2 className="card__title">
                <span className="card__title-icon">📜</span>
                Analysis History
            </h2>
            {history.length > 0 ? (
                <table className="density-table" style={{ marginTop: '1rem' }}>
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Date</th>
                            <th>Overall Score</th>
                            <th>ATS Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map((item, index) => (
                            <tr key={index}>
                                <td>{item.filename}</td>
                                <td>{formatDate(item.analyzed_at)}</td>
                                <td>
                                    <span style={{ color: getScoreColor(item.overall_score), fontWeight: 600 }}>
                                        {item.overall_score}%
                                    </span>
                                </td>
                                <td>{item.ats_score}%</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <div className="empty-state">
                    <div className="empty-state__icon">📭</div>
                    <p className="empty-state__text">No analysis history yet. Upload a resume to get started!</p>
                </div>
            )}
        </div>
    )

    return (
        <div className="app">
            {/* Copy Notification Toast */}
            {copyNotification && (
                <div className="copy-notification">
                    ✅ {copyNotification}
                </div>
            )}

            {/* Theme Toggle */}
            <div className="theme-toggle">
                <button
                    className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                    onClick={() => setTheme('dark')}
                    title="Dark Mode"
                >
                    🌙
                </button>
                <button
                    className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                    onClick={() => setTheme('light')}
                    title="Light Mode"
                >
                    ☀️
                </button>
            </div>

            {/* Header */}
            <header className="header">
                <span className="header__badge">✨ Pro Edition</span>
                <h1 className="header__title">Resume ATS Analyzer</h1>
                <p className="header__subtitle">
                    Get detailed insights on how your resume performs against Applicant Tracking Systems and land more interviews
                </p>
            </header>

            {/* Navigation */}
            <nav className="nav-tabs">
                <button
                    className={`nav-tab ${activeView === 'analyzer' ? 'active' : ''}`}
                    onClick={() => setActiveView('analyzer')}
                >
                    🔍 Analyzer
                </button>
                <button
                    className={`nav-tab ${activeView === 'tips' ? 'active' : ''}`}
                    onClick={() => setActiveView('tips')}
                >
                    💡 Tips
                </button>
                <button
                    className={`nav-tab ${activeView === 'history' ? 'active' : ''}`}
                    onClick={() => { setActiveView('history'); fetchHistory(); }}
                >
                    📜 History
                </button>
            </nav>

            {/* Main Content */}
            {activeView === 'analyzer' && renderAnalyzer()}
            {activeView === 'tips' && renderTips()}
            {activeView === 'history' && renderHistory()}

            {/* Footer */}
            <footer className="footer">
                <div className="footer__links">
                    <a href="#" className="footer__link">About</a>
                    <a href="#" className="footer__link">Privacy</a>
                    <a href="#" className="footer__link">Contact</a>
                </div>
                <p>Resume ATS Analyzer Pro — Improve your chances of getting noticed</p>
            </footer>
        </div>
    )
}

export default App
