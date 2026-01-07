# 📄 Resume ATS Analyzer Pro

A professional, full-stack web application that analyzes resumes against job descriptions and provides detailed ATS (Applicant Tracking System) compatibility scores, keyword analysis, and actionable suggestions.

![Version](https://img.shields.io/badge/version-2.1.0-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-green) ![React](https://img.shields.io/badge/React-18.2-61DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688) ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248)

---

## ✨ Features

### 🎯 Core Functionality
- **Resume Analysis**: Upload PDF or DOCX resumes for comprehensive analysis
- **ATS Score Calculation**: Get a detailed compatibility score against job descriptions
- **Keyword Matching**: Identify matched and missing keywords from job postings
- **Smart Suggestions**: Receive actionable recommendations to improve your resume

### 📊 Advanced Analysis
- **Section Detection**: Automatically identifies resume sections (Experience, Education, Skills, etc.)
- **Formatting Analysis**: Evaluates resume formatting for ATS compatibility
- **Content Similarity Scoring**: Measures how well your resume aligns with the job description
- **Industry-Specific Keywords**: Access keyword suggestions for various industries

### 💾 Data Persistence
- **MongoDB Atlas Integration**: All analyses are stored in the cloud
- **Analysis History**: View past analyses with detailed breakdowns
- **Statistics Dashboard**: Track your improvement over time

### 🎨 User Experience
- **Modern UI**: Clean, responsive React-based interface
- **Dark/Light Theme**: Toggle between visual modes
- **Sample Job Descriptions**: Quick testing with pre-built job samples
- **Resume Tips**: Professional advice for resume optimization

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python web framework |
| **Uvicorn** | ASGI server for running the application |
| **Motor** | Async MongoDB driver for Python |
| **PDFMiner** | PDF text extraction |
| **python-docx** | DOCX file processing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | Component-based UI library |
| **Vite** | Next-generation frontend build tool |
| **Axios** | HTTP client for API requests |
| **CSS3** | Modern styling with animations |

### Database
| Technology | Purpose |
|------------|---------|
| **MongoDB Atlas** | Cloud-hosted NoSQL database |

---

## 📁 Project Structure

```
MiniProj/
├── backend/
│   ├── main.py           # FastAPI application and routes
│   ├── database.py       # MongoDB connection and operations
│   ├── utils.py          # Resume analysis utilities
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main React component
│   │   └── index.css     # Styles
│   ├── index.html        # Entry HTML file
│   ├── package.json      # Node.js dependencies
│   └── vite.config.js    # Vite configuration
└── README.md             # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed
- **Node.js 18+** installed
- **MongoDB Atlas** account (for database)

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/UtkarshDivate95/MiniProject.git
cd MiniProject
```

#### 2️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3️⃣ Configure MongoDB

Create a `.env` file in the `backend` directory (if not using environment variables):

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/resume_ats?retryWrites=true&w=majority
```

#### 4️⃣ Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

---

## 🏃 Running the Application

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The application will be available at: `http://localhost:5173`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API health check and info |
| `POST` | `/analyze` | Analyze uploaded resume |
| `POST` | `/quick-score` | Analyze pasted text |
| `GET` | `/history` | Get analysis history |
| `GET` | `/history/{id}` | Get specific analysis |
| `DELETE` | `/history/{id}` | Delete specific analysis |
| `DELETE` | `/history` | Clear all history |
| `GET` | `/stats` | Get analysis statistics |
| `GET` | `/tips` | Get resume writing tips |
| `GET` | `/industries` | Get industry keywords |
| `GET` | `/sample-jobs` | Get sample job descriptions |

---

## 📖 Usage

1. **Open the Application**: Navigate to `http://localhost:5173` in your browser
2. **Upload Resume**: Drag and drop or select a PDF/DOCX file
3. **Enter Job Description**: Paste the job posting you're applying for
4. **Analyze**: Click the analyze button to get your ATS score
5. **Review Results**: Examine matched/missing keywords and suggestions
6. **Improve**: Use the suggestions to optimize your resume

---

## 🏭 Supported Industries

The application provides keyword suggestions for:
- 💻 Software Engineering
- 📊 Data Science & Analytics
- 📦 Product Management
- 📈 Marketing
- 🎨 UX/UI Design
- 💰 Finance & Accounting

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ using FastAPI and React
- Inspired by the need for transparent ATS analysis tools
- Thanks to the open-source community for the amazing libraries

---

<p align="center">
  Made with ⚡ by Utkarsh
</p>
