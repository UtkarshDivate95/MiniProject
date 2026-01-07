"""
FastAPI Backend for Resume ATS Analyzer - Professional Edition
With MongoDB Atlas Integration
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import json

from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    generate_full_analysis,
)
from database import (
    connect_to_mongodb,
    close_mongodb_connection,
    save_analysis,
    get_analysis_history,
    get_analysis_by_id,
    delete_analysis,
    clear_all_history,
    get_total_analyses_count,
    get_analyses_stats,
)


# Lifespan context manager for MongoDB connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Connect to MongoDB
    await connect_to_mongodb()
    yield
    # Shutdown: Close MongoDB connection
    await close_mongodb_connection()


app = FastAPI(
    title="Resume ATS Analyzer Pro",
    description="Professional Resume Analysis with ATS Scoring, Keyword Analysis, and Detailed Suggestions - With MongoDB Atlas",
    version="2.1.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Resume ATS Analyzer Pro API is running with MongoDB Atlas.",
        "version": "2.1.0",
        "database": "MongoDB Atlas",
        "endpoints": {
            "analyze": "POST /analyze - Analyze resume against job description",
            "quick_score": "POST /quick-score - Quick scoring without file upload",
            "history": "GET /history - Get analysis history from database",
            "history_detail": "GET /history/{id} - Get specific analysis by ID",
            "delete_analysis": "DELETE /history/{id} - Delete specific analysis",
            "clear_history": "DELETE /history - Clear all history",
            "stats": "GET /stats - Get analysis statistics",
            "tips": "GET /tips - Get resume writing tips",
            "industries": "GET /industries - Get industry-specific keywords"
        }
    }


@app.get("/tips")
async def get_resume_tips():
    """Returns professional resume writing tips."""
    return {
        "tips": [
            {
                "category": "Keywords",
                "title": "Mirror the Job Description",
                "description": "Use exact phrases and keywords from the job posting in your resume."
            },
            {
                "category": "Keywords",
                "title": "Include Industry Buzzwords",
                "description": "Research and include relevant industry-specific terminology."
            },
            {
                "category": "Format",
                "title": "Use Standard Section Headers",
                "description": "Stick to traditional headers like 'Experience', 'Education', 'Skills' for ATS compatibility."
            },
            {
                "category": "Format",
                "title": "Avoid Tables and Graphics",
                "description": "ATS systems often struggle with complex formatting. Keep it simple."
            },
            {
                "category": "Format",
                "title": "Use Standard Fonts",
                "description": "Stick to Arial, Calibri, or Times New Roman for best ATS parsing."
            },
            {
                "category": "Content",
                "title": "Quantify Achievements",
                "description": "Use numbers and percentages to demonstrate impact (e.g., 'Increased sales by 30%')."
            },
            {
                "category": "Content",
                "title": "Start with Action Verbs",
                "description": "Begin each bullet point with strong action verbs like Led, Developed, Achieved."
            },
            {
                "category": "Content",
                "title": "Tailor for Each Application",
                "description": "Customize your resume for each job application to match specific requirements."
            },
            {
                "category": "Length",
                "title": "Keep It Concise",
                "description": "1 page for early career, 2 pages for experienced professionals."
            },
            {
                "category": "Technical",
                "title": "Save as PDF or DOCX",
                "description": "These formats preserve formatting and are ATS-friendly."
            }
        ]
    }


@app.get("/industries")
async def get_industry_keywords():
    """Returns common keywords for different industries/roles."""
    return {
        "industries": {
            "software_engineering": {
                "name": "Software Engineering",
                "keywords": [
                    "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
                    "CI/CD", "Agile", "Scrum", "Git", "REST API", "Microservices", "SQL",
                    "System Design", "Testing", "DevOps", "Cloud", "Full Stack", "Backend"
                ]
            },
            "data_science": {
                "name": "Data Science & Analytics",
                "keywords": [
                    "Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow",
                    "PyTorch", "Pandas", "NumPy", "Data Visualization", "Tableau", "Power BI",
                    "Statistics", "A/B Testing", "NLP", "Computer Vision", "Big Data", "Spark"
                ]
            },
            "product_management": {
                "name": "Product Management",
                "keywords": [
                    "Product Strategy", "Roadmap", "User Research", "A/B Testing", "Agile",
                    "Scrum", "JIRA", "Cross-functional", "Stakeholder Management", "KPIs",
                    "MVP", "User Stories", "Sprint Planning", "Product Discovery", "Analytics"
                ]
            },
            "marketing": {
                "name": "Marketing",
                "keywords": [
                    "Digital Marketing", "SEO", "SEM", "Content Marketing", "Social Media",
                    "Analytics", "Google Analytics", "Campaign Management", "Brand Strategy",
                    "Email Marketing", "PPC", "Conversion Rate", "ROI", "Marketing Automation"
                ]
            },
            "design": {
                "name": "UX/UI Design",
                "keywords": [
                    "Figma", "Sketch", "Adobe XD", "User Research", "Wireframing", "Prototyping",
                    "Design Systems", "Usability Testing", "Information Architecture", "Interaction Design",
                    "Visual Design", "Accessibility", "Responsive Design", "Design Thinking"
                ]
            },
            "finance": {
                "name": "Finance & Accounting",
                "keywords": [
                    "Financial Analysis", "Budgeting", "Forecasting", "Excel", "Financial Modeling",
                    "GAAP", "Auditing", "Compliance", "Risk Management", "SAP", "QuickBooks",
                    "Account Reconciliation", "Financial Reporting", "Variance Analysis", "Taxation"
                ]
            }
        }
    }


@app.get("/sample-jobs")
async def get_sample_job_descriptions():
    """Returns sample job descriptions for testing the analyzer."""
    return {
        "samples": [
            {
                "id": "software_engineer",
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "description": """We are looking for a Senior Software Engineer to join our team.

Requirements:
- 5+ years of experience in software development
- Strong proficiency in Python, JavaScript, and React
- Experience with AWS, Docker, and Kubernetes
- Familiarity with microservices architecture and REST APIs
- Experience with SQL and NoSQL databases (PostgreSQL, MongoDB)
- Knowledge of CI/CD pipelines and DevOps practices
- Strong problem-solving and communication skills
- Experience with Agile/Scrum methodologies

Responsibilities:
- Design and implement scalable backend services
- Lead code reviews and mentor junior developers
- Collaborate with product managers and designers
- Optimize application performance and reliability
- Write clean, maintainable, and well-documented code

Nice to have:
- Experience with machine learning or data engineering
- Knowledge of TypeScript and Node.js
- Contributions to open-source projects"""
            },
            {
                "id": "data_analyst",
                "title": "Data Analyst",
                "company": "Analytics Inc",
                "description": """Join our data team as a Data Analyst!

Requirements:
- 3+ years of experience in data analysis
- Expert-level SQL and Excel skills
- Proficiency in Python or R for data analysis
- Experience with Tableau, Power BI, or similar tools
- Strong statistical analysis and hypothesis testing skills
- Experience with A/B testing and experimentation
- Excellent presentation and storytelling with data
- Bachelor's degree in Statistics, Mathematics, or related field

Responsibilities:
- Analyze large datasets to identify trends and insights
- Build dashboards and reports for stakeholders
- Collaborate with product and engineering teams
- Define KPIs and success metrics
- Present findings to leadership team

Nice to have:
- Experience with Google Analytics
- Knowledge of machine learning basics
- Experience with BigQuery or Snowflake"""
            },
            {
                "id": "product_manager",
                "title": "Product Manager",
                "company": "Innovation Labs",
                "description": """We're seeking a Product Manager to drive product strategy.

Requirements:
- 4+ years of product management experience
- Strong understanding of Agile and Scrum methodologies
- Experience with JIRA, Confluence, and roadmap tools
- Excellent stakeholder management and communication
- Data-driven decision making with analytics tools
- Experience conducting user research and interviews
- Technical background or ability to work with engineers
- MBA or equivalent experience preferred

Responsibilities:
- Define product vision and strategy
- Create and prioritize product backlog
- Write user stories and acceptance criteria
- Launch features and measure success with KPIs
- Collaborate with design, engineering, and marketing

Nice to have:
- Experience in SaaS or B2B products
- Knowledge of SQL for data analysis
- Experience with growth and experimentation"""
            },
            {
                "id": "marketing_manager",
                "title": "Digital Marketing Manager",
                "company": "Growth Co",
                "description": """Looking for a Digital Marketing Manager to lead our marketing efforts.

Requirements:
- 5+ years in digital marketing
- Expert in SEO, SEM, and PPC campaigns
- Experience with Google Analytics and Google Ads
- Proficiency in marketing automation tools (HubSpot, Marketo)
- Strong content marketing and social media skills
- Experience with email marketing and conversion optimization
- Knowledge of CRM systems (Salesforce preferred)
- Strong analytical and ROI measurement skills

Responsibilities:
- Develop and execute digital marketing strategy
- Manage paid advertising campaigns and budget
- Optimize website for SEO and conversions
- Create compelling content for multiple channels
- Analyze campaign performance and provide insights

Nice to have:
- Experience with video marketing
- Knowledge of marketing analytics platforms
- Brand management experience"""
            },
            {
                "id": "ux_designer",
                "title": "Senior UX Designer",
                "company": "Design Studio",
                "description": """Join us as a Senior UX Designer to create exceptional user experiences.

Requirements:
- 5+ years of UX/UI design experience
- Expert in Figma, Sketch, and Adobe Creative Suite
- Strong portfolio demonstrating user-centered design
- Experience with user research and usability testing
- Knowledge of design systems and component libraries
- Proficiency in prototyping and wireframing tools
- Understanding of accessibility standards (WCAG)
- Experience working in Agile teams

Responsibilities:
- Lead user research and synthesize insights
- Create wireframes, prototypes, and high-fidelity designs
- Build and maintain design systems
- Collaborate with product managers and engineers
- Conduct usability testing and iterate on designs

Nice to have:
- Experience with motion design and micro-interactions
- Knowledge of HTML/CSS for design handoff
- Experience with mobile app design"""
            }
        ]
    }


@app.get("/history")
async def get_history(limit: int = 10):
    """Returns the most recent analyses from MongoDB (most recent first)."""
    try:
        history = await get_analysis_history(limit=limit)
        total = await get_total_analyses_count()
        return {
            "history": history,
            "total_analyses": total
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history: {str(e)}"
        )


@app.get("/history/{analysis_id}")
async def get_single_analysis(analysis_id: str):
    """Get a specific analysis by ID."""
    try:
        analysis = await get_analysis_by_id(analysis_id)
        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching analysis: {str(e)}"
        )


@app.delete("/history/{analysis_id}")
async def delete_single_analysis(analysis_id: str):
    """Delete a specific analysis by ID."""
    try:
        success = await delete_analysis(analysis_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )
        return {"message": "Analysis deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting analysis: {str(e)}"
        )


@app.delete("/history")
async def clear_history():
    """Clears all analysis history from MongoDB."""
    try:
        deleted_count = await clear_all_history()
        return {
            "message": "History cleared successfully",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing history: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """Get statistics about all analyses."""
    try:
        stats = await get_analyses_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stats: {str(e)}"
        )


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Performs comprehensive resume analysis against a job description.
    Returns detailed ATS score, keyword analysis, section detection, and suggestions.
    """
    # Validate file type
    filename = resume.filename.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF or DOCX file.",
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    # Read file content
    file_bytes = await resume.read()

    # Extract text based on file type
    try:
        if filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_bytes)
        else:
            resume_text = extract_text_from_docx(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}",
        )

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the resume. The file might be image-based or corrupted.",
        )

    # Generate comprehensive analysis
    try:
        analysis = generate_full_analysis(resume_text, job_description)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}",
        )

    # Prepare response
    result = {
        "filename": resume.filename,
        "analyzed_at": datetime.now().isoformat(),
        **analysis
    }

    # Store in MongoDB
    try:
        history_entry = {
            "filename": resume.filename,
            "analyzed_at": result["analyzed_at"],
            "overall_score": analysis["overall_score"],
            "ats_score": analysis["ats_score"],
            "section_score": analysis.get("section_score", 0),
            "formatting_score": analysis.get("formatting_score", 0),
            "content_similarity_score": analysis.get("content_similarity_score", 0),
            "matched_keywords_count": len(analysis.get("matched_keywords", [])),
            "missing_keywords_count": len(analysis.get("missing_keywords", [])),
        }
        doc_id = await save_analysis(history_entry)
        result["_id"] = doc_id
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to save analysis to database: {e}")

    return result


@app.post("/quick-score")
async def quick_score(
    resume_text: str = Form(...),
    job_description: str = Form(...),
):
    """
    Quick scoring endpoint for pasted resume text (no file upload).
    Useful for testing or quick iterations.
    """
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume text cannot be empty.",
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    analysis = generate_full_analysis(resume_text, job_description)
    
    return {
        "source": "text_input",
        "analyzed_at": datetime.now().isoformat(),
        **analysis
    }
